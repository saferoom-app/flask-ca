# Import section
import json,datetime,time
from flask import Blueprint, abort,request,render_template,jsonify, Response
from sqlalchemy import desc
from webapp.core.decorators import process_request
from webapp.models import db,CertificateAuthority, Key, Certificate, CRL
from dateutil.relativedelta import relativedelta
import webapp.config.caconfig as config

# Define the Blueprint
mod_ca = Blueprint('mod_ca', __name__, url_prefix='/ca')

def get_root_ca(id,cas):
    for ca in cas:
        if id == ca.id:
            return ca.name
    return "n/a"

# Routes
@mod_ca.route("/",methods=["POST","GET"])
def ca_index_page():
    return render_template("mod_ca/index.html",active="ca")

@mod_ca.route("/view/<string:caid>/",methods=["GET"])
def view_ca(caid):
    return render_template("mod_ca/view.html",active="ca",caid=caid)

@mod_ca.route("/list",methods=["POST"])
def list_ca():

    # Getting filter
    data = request.get_json()
    result = CertificateAuthority.query.with_entities(CertificateAuthority.id,CertificateAuthority.name,CertificateAuthority.dscr,CertificateAuthority.root_ca)
    if data['search']:
        result = result.filter(CertificateAuthority.name.ilike("%"+data['search']+"%"))

    # Prepare and send response
    cas = []
    for ca in result:
        cas.append({"id":ca.id,"name":ca.name,"description":ca.dscr,"root_ca":get_root_ca(ca.root_ca,result)})

    return jsonify(cas=cas)

@mod_ca.route("/tree",methods=["GET"])
def build_tree():

    flare = {}
    flare['name'] = 'CA Root Element'
    flare['ID'] = 0
    
    # Getting a list of CAs (only ID and Name)
    result = CertificateAuthority.query.with_entities(CertificateAuthority.id,CertificateAuthority.name,CertificateAuthority.root_ca).all()
    for ca in result:
        assign_ca(flare,ca)
    
    return json.dumps(flare)

@mod_ca.route("/create",methods=["POST"])
@process_request
def create_ca():
    '''
		Function is used to create new CA (Root or Subordinate). If we're creating the Subordinate CA, we need to specify the "root_ca". By default it's None
    '''
    from OpenSSL import crypto, SSL

    # Parsing request
    data = request.get_json()

    # Creating new CA
    ca = CertificateAuthority(name=data['name'],subject_dn=json.dumps(data['subjectDN']))
    ca.dscr = data['dscr']
    ca.extensions = json.dumps(data['extensions'])

    # If Root CA is specified we need to get its key
    root_key = None
    root_cert = None
    if data['root_ca']['ca_id'] > 0:
    	key = Key.query.get(data['root_ca']['ca_id'])
    	if not key:
    		abort(config.http_notfound,{"message":config.error_rootca_notfound % str(data['root_ca']['ca_id'])})   
        try:
    	    # Getting CA key
    	    root_key = crypto.load_privatekey(crypto.FILETYPE_PEM,key.private,passphrase=str(data['root_ca']['pass']))
    	    root_cert = crypto.load_certificate(crypto.FILETYPE_PEM,key.public)

            # Setting the Root ca
            ca.set_root(data['root_ca']['ca_id'])
        except Exception as e:
            abort(config.http_notauthorized,{"message":config.error_pass_incorrect})
    
    # Adding the CA to the database
    db.session.add(ca)
    db.session.commit()

    # Creating a pair of keys
    key = Key()
    key.expires_in = datetime.datetime.now() + relativedelta(months=data['valid'])
    key.generate_private_key(data['pass'],data['keylen'])
    key.generate_public_key(data,root_key,root_cert,ca.id)    
        
    # Adding to database
    ca.keys.append(key)
    db.session.add(key)
    db.session.commit()

    return jsonify(message=config.msg_ca_created),config.http_created

# Getting CA information 
@mod_ca.route("/get/<string:id>",methods=["GET"])
def get_ca(id):

    # Getting CA information
    result = CertificateAuthority.query.get(id)
    if not result:
        abort(config.http_notfound,{"message":config.error_ca_notfound})

    # Getting a list of CRLS
    crls = result.crls

    # Getting Certificate Authority Private Key
    key = result.keys[0]
    if not key:
        abort(config.http_notfound,{"message":config.error_pkey_notfound})

    ca = result.list_dict()
    ca['crls'] = []
    
    for crl in crls:
        ca['crls'].append({"id":crl.id,"created":crl.created})
    ca['expires'] = time.mktime(key.expires_in.timetuple())
    return jsonify(ca=ca)

# Route used to handle OCSP requests
@mod_ca.route("/<string:caid>/ocsp",methods=["POST","GET"])
def handle_ocsp_requests(caid):

    # Import section (specifically for OCSP)
    from asn1crypto.util import timezone
    from asn1crypto.ocsp import OCSPRequest
    from oscrypto import asymmetric
    from ocspbuilder import OCSPResponseBuilder
    
    # Getting CA information
    key = Key.query.filter_by(ca=caid).first()
    if not key:
        abort(config.http_notfound,{"message":config.error_pkey_notfound})
    private,public = key.dump(config.path_keys)
    with open(private,"rb") as f:
        issuer_key = asymmetric.load_private_key(f.read(),"testtest")
    with open(public,"rb") as f:
        issuer_cert = asymmetric.load_certificate(f.read())

    # Parsing the OCSP request
    ocsp = OCSPRequest.load(request.get_data())
    tbs_request = ocsp['tbs_request']
    request_list = tbs_request['request_list']
    if len(request_list) != 1:
        abort(config.http_notimplemented,{"message":config.error_multiple_requests})
    single_request = request_list[0]  # TODO: Support more than one request
    req_cert = single_request['req_cert']
    serial = hex(req_cert['serial_number'].native)[2:]

    # Getting certificate
    cert = Certificate.query.filter_by(serial=serial).first()
    if not cert:
        abort(config.http_notfound,{"message":config.error_cert_notfound})
    cert_path = cert.dump(config.path_keys)
    with open(cert_path,"rb") as f:
        subject_cert = asymmetric.load_certificate(f.read())

    # A response for a certificate in good standing
    builder = OCSPResponseBuilder(u'successful', subject_cert, u'good')
    ocsp_response = builder.build(issuer_key, issuer_cert)
    return ocsp_response.dump()   

# Route used to provide the latest CRL (CDP value)
@mod_ca.route("/<string:caid>/crl/full",methods=["GET"])
def get_latest_crl(caid):

    # Import section
    import base64
    
    # Getting the latest CRL object
    crl = CRL.query.filter_by(ca=caid).order_by(desc(CRL.created)).limit(1).first()
    if not crl:
        abort(config.http_notfound,{"message":config.error_crl_notfound})

    # Sending response
    response = Response(base64.b64decode(crl.crl))
    response.headers['Content-Type'] = config.MIME_CRL
    response.headers['Content-Disposition'] = "attachment; filename=%s.crl;" % crl.id
    return response

# Route used to generate CRL
@mod_ca.route("/<string:caid>/crl/generate",methods=["POST"])
@process_request
def generate_full_crl(caid):
    '''
        This route is used to generate the full CRL. The procedure works like the following:

            1. App connects to database
            2. App queries a list of certificates bound to this CA with status "Revoked" (2)
            3. App generates CRL and puts this CRL into database
    '''

    # Import section
    from OpenSSL import crypto, SSL

    # Getting data
    data = request.get_json()

    # Getting CA
    ca = CertificateAuthority.query.get(caid)
    if not ca:
        abort(config.http_notfound,{"message":config.error_ca_notfound})

    # Getting the CA Key, that will be used to sign certificates
    key = ca.keys[0]
    if not key:
        abort(config.http_notfound,{"message":config.error_pkey_notfound})
    try:
        private_key = crypto.load_privatekey(crypto.FILETYPE_PEM,key.private,passphrase=str(data['pass']))
        public_key = crypto.load_certificate(crypto.FILETYPE_PEM,key.public)
    except Exception as e:
        abort(config.http_notauthorized,{"message":config.error_pass_incorrect})

    # Getting a list of certificates with Revoked status
    result = Certificate.query.with_entities(Certificate.serial,Certificate.code_revoke).filter( (Certificate.status==config.STATUS_REVOKED) | (Certificate.status==config.STATUS_PAUSED) ).all()
        
    # Starting the generate CRL
    crl = crypto.CRL()

    for cert in result:
        revoked = crypto.Revoked()
        revoked.set_rev_date(datetime.datetime.now().strftime("%Y%m%d%H%M%SZ").encode("ascii"))
        revoked.set_reason(revoked.all_reasons()[cert.code_revoke])
        revoked.set_serial(str(cert.serial[:-1]))
        crl.add_revoked(revoked)

    # Creating new CRL
    crlObject = CRL()
    crlObject.created = datetime.datetime.utcnow()
    crlObject.crl = crl.export(public_key,private_key,crypto.FILETYPE_ASN1,\
        days=config.CRL_VALID_DAYS,digest=b'sha256')
    ca.crls.append(crlObject)
    db.session.add(crlObject)
    db.session.commit()
    return jsonify(message=config.msg_crl_generated),config.http_created

@mod_ca.route("/<string:caid>/crl/list",methods=["GET"])
def list_crls(caid):

    # Getting a list of CRLs
    result = CRL.query.filter_by(ca=caid).all()

    # Generating a list of CRLs
    crls = []
    for crl in result:
        crls.append({"id":crl.id,"created":crl.created})
    
    # Sending response
    return jsonify(crls=crls)

@mod_ca.route("/crl/get/<string:crlid>",methods=["GET"])
def download_crl(crlid):

    # Getting CRL
    crl = CRL.query.get(crlid)
    if not crl:
        abort(config.http_notfound,{"message":config.error_crl_notfound})

    # Sending response
    response = Response(crl.crl)
    response.headers['Transfer-Encoding'] = config.ENCODING_CHUNKED
    response.headers['Content-Type'] = config.MIME_CRL
    response.headers['Content-Disposition'] = "attachment; filename=%s.crl;" % crl.id
    return response

@mod_ca.route("/crl/delete/<string:crlid>",methods=["DELETE"])
def delete_crls(crlid):

    # Getting the CRL to be deleted
    crl = CRL.query.get(crlid)
    if not crl:
        abort(config.http_notfound,{"message":config.error_crl_notfound})

    # Deleting found CRL
    db.session.delete(crl)
    db.session.commit()

    # Sending response
    return jsonify(message=config.msg_crl_deleted),config.http_ok

@mod_ca.route("/<string:caid>/crt")
def download_crt(caid):

    # Getting CA information
    ca = CertificateAuthority.query.get(caid)
    if not ca:
        abort(config.http_notfound,{"message":config.error_ca_notfound})

    key = ca.keys[0]
    if not key:
        abort(config.http_notfound,{"message":config.error_pkey_notfound})        

    # Sending response
    response = Response(key.public)
    response.headers['Content-Type'] = config.MIME_CACERT
    response.headers['Content-Disposition'] = "attachment; filename=%s.crt;" % ca.name
    return response

@mod_ca.route("/<string:caid>/pkey")
def download_private(caid):

    # Getting CA information
    ca = CertificateAuthority.query.get(caid)
    if not ca:
        abort(config.http_notfound,{"message":config.error_ca_notfound})

    key = ca.keys[0]
    if not key:
        abort(config.http_notfound,{"message":config.error_pkey_notfound})        

    # Sending response
    response = Response(key.private)
    response.headers['Content-Type'] = config.MIME_PEM
    response.headers['Content-Disposition'] = "attachment; filename=%s.pem;" % ca.name
    return response

@mod_ca.route("/<string:caid>/delete",methods=["DELETE"])
@process_request
def delete_ca(caid):

    # Import section
    from OpenSSL import crypto, SSL

    # Getting JSON data
    data = request.get_json()

    # Getting CA information
    ca = CertificateAuthority.query.get(caid)
    if not ca:
        abort(config.http_notfound,{"message":config.error_ca_notfound})

    key = ca.keys[0]
    if not key:
        abort(config.http_notfound,{"message":config.error_pkey_notfound})

    # Checking that provided password was OK
    try:
        private_key = crypto.load_privatekey(crypto.FILETYPE_PEM,key.private,passphrase=str(data['pass']))
    except Exception as e:
        abort(config.http_notauthorized,{"message":config.error_pass_incorrect})

    # Deleting CA certificates, keys and CRLs
    db.session.delete(ca)
    db.session.commit()
    return jsonify(message=config.msg_ca_deleted),config.http_ok

def assign_ca(data,rawCA):
    if data['ID'] == rawCA.root_ca:
        # We want a list to assign the CA to
        if not 'children' in data:
            data['children'] = []
        data['children'].append(create_CA(rawCA))
        return True

    elif 'children' in data:
        # Not our root? Let's see your children
        for childCA in data['children']:
            if assign_ca(childCA, rawCA):
                # CA already assigned
                # No need to dive deeper into the tree
                break
    else:
        # Sorry, I'm not your root and I have no children
        return False

def create_CA(obj):
    CA = {}
    CA['ID'] = obj.id
    CA['name'] = obj.name
    return CA