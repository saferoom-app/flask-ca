# Import section
from flask import Blueprint, jsonify,abort,request,render_template,Response
import app.config.caconfig as config
from app.core.models import Certificate,CertificateAuthority, Template, User, Key
from app.classes.CertificateRequest import CertificateRequest
from app.core.decorators import process_request
from app.core.database import db_session
from app.core.functions import write_status,get_status,remove_status,force_bytes
from OpenSSL import crypto,rand
import time, datetime

# Initializing the blueprint
mod_certificates = Blueprint("mod_certificates",__name__,url_prefix='/certificates')

# Routes
@mod_certificates.route("/",methods=["GET"])
def index_certificates():
    
    # Getting a list of Certificate Authorities
    cas = []
    result = CertificateAuthority.query.with_entities(CertificateAuthority.id,CertificateAuthority.name)
    for ca in result:
    	cas.append({"id":ca.id,"name":ca.name})

    return render_template("mod_certificates/index.html",active="cert",statuses=config.statuses,cas=cas)

@mod_certificates.route("/list",methods=["POST"])
@process_request
def list_certificates():

    # Import section
    from math import ceil
    
    # Getting filter
    data = request.get_json()
    
    # Creating query
    query = Certificate.query.with_entities(Certificate.id,Certificate.name,Certificate.status,Certificate.code_revoke,Certificate.reason_revoke,Certificate.serial).filter(Certificate.name.ilike("%"+data['search']+"%"))
    
    # Getting a list of certificates (first, without filters)
    if data['ca']:
    	query = query.filter(Certificate.ca.in_(data['ca']))
    if data['status']:
    	query = query.filter(Certificate.status.in_(data['status']))

    certificates = []
    
    # Calculating the total number
    total = query.count()

    # Adding the LIMIT function
    query = query.limit(config.ITEMS_PER_PAGE).offset((data['page']-1)*config.ITEMS_PER_PAGE)

    result = query.all()
    for cert in result:
        certificates.append({"id":cert.id,"name":cert.name,"status":cert.status,"code":config.reasons[str(cert.code_revoke)],"reason":cert.reason_revoke,"serial":cert.serial})
    return jsonify(certificates=certificates,\
        reasons=config.reasons,\
        pages=int(ceil(float(total) / config.ITEMS_PER_PAGE)),\
        current=data['page'])

@mod_certificates.route("/create",methods=["GET"])
def index_create_certificates():
    
    # Getting a list of created Certificate Authorities
    result = CertificateAuthority.query.all()
    cas = [{"id":ca.id,"name":ca.name} for ca in result]

    # Getting a list of templates
    result = Template.query.all()
    tpls = [{"id":tpl.id,"name":tpl.name} for tpl in result]    

    return render_template("mod_certificates/create.html",active="cert",tpls=tpls,cas=cas)

@mod_certificates.route("/generate",methods=["POST"])
@process_request
def generate_certificates():

    # Getting data
    data = request.get_json()
    valid = 0
    index = 0    

    # Writing status
    write_status(data['sid'],{"status":"Initializing","value":0},path=config.path_status)
                
    # Listing the request objects
    for item in data['certificates']:

        # Getting user information
        user = User.query.get(item['uid'])
        if not user:
            abort(config.http_notfound,{"message":config.error_user_notfound})
        
        # Getting CA information
        ca = CertificateAuthority.query.get(item['ca'])
        if not ca:
            abort(config.http_notfound,{"message":config.error_ca_notfound})

        # Getting Certificate Authority Private Key
        key = Key.query.filter_by(ca=item['ca']).first()
        if not key:
            abort(config.http_notfound,{"message":config.error_pkey_notfound})

        # Trying to load the Private Key and decrypt it with the password
        try:
            private_key = crypto.load_privatekey(crypto.FILETYPE_PEM,key.private,passphrase=str(data['pass']))
            public_key = crypto.load_certificate(crypto.FILETYPE_PEM,key.public) 
        except Exception as e:
            abort(config.http_badrequest,{"message":config.error_pkey_password})

        # Getting Template
        template = Template.query.get(item['tpl'])
        if not template:
            abort(config.http_notfound,{"message":config.error_template_notfound})

        
        # Writing status
        write_status(data['sid'],{"status":config.status_generate_cert % user.name,"value":index},path=config.path_status)
                
        cert_request = CertificateRequest()
        cert_request.set_subject(user.subject)
        cert_request.set_valid(item['valid'],key.expires_in)
        cert_request.set_extensions(ca,template,config.extensions)
        certificate = cert_request.generate(private_key,public_key,item['pass'])
        certificate.name = user.name
        certificate.authority = ca
        db_session.add(certificate)
        db_session.commit()

    # Clearing status messages
    remove_status(data['sid'],path=config.path_status)
    return jsonify(message=config.msg_certificates_generated),config.http_created

@mod_certificates.route("/revoke",methods=["POST"])
@process_request
def revoke_certificates():

    # Getting JSON data
    data = request.get_json()

    # Getting a list of certificates to be revoked
    result = Certificate.query.filter(Certificate.id.in_(data['certs'])).all()
    for cert in result:
        if cert.status == config.STATUS_ACTIVE:
            if data['reason'] == 6:
                cert.status = config.STATUS_PAUSED
            else:
                cert.status = config.STATUS_REVOKED
            cert.code_revoke = data['reason']
            cert.reason_revoke = data['comment']
            cert.date_revoke = datetime.datetime.now()
    db_session.commit()
    

    return jsonify(message=config.msg_certs_revoked),config.http_ok

### Downloading the PFX
@mod_certificates.route("/download/<string:id>")
def get_pfx(id):
    
    # Import
    import base64

    # Getting certificate
    cert = Certificate.query.get(id)
    if not cert:
        abort(config.http_notfound,{"message":""})

    # Generating response
    response = Response(cert.p12)
    response.headers['Content-Type'] = config.MIME_PFX
    response.headers['Content-Disposition'] = "attachment; filename=%s.pfx;" % cert.name
    return response

### Downloading the PFX
@mod_certificates.route("/download/public/<string:id>")
def get_public_key(id):

    import base64

    # Getting certificate
    cert = Certificate.query.get(id)
    if not cert:
        abort(config.http_notfound,{"message":config.error_cert_notfound})   
    
    response = Response(cert.public)
    response.headers['Content-Type'] = config.MIME_PEM
    response.headers['Content-Disposition'] = "attachment; filename=%s.pem;" % cert.name
    return response

@mod_certificates.route("/test",methods=["GET","POST"])
def generate_crl():

    # Getting a list of certificates
    result = Certificate.query.with_entities(Certificate.serial).all()
    crl = crypto.CRL()

    # Getting the CA information
    key = Key.query.filter_by(ca=1).first()
    private_key = crypto.load_privatekey(crypto.FILETYPE_PEM,key.private,passphrase="testtest")
    public_key = crypto.load_certificate(crypto.FILETYPE_PEM,key.public)

    for cert in result:
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%SZ").encode("ascii")
        revoked = crypto.Revoked()
        revoked.set_rev_date(now)
        revoked.set_reason(revoked.all_reasons()[1])
        revoked.set_serial(str(cert.serial[:-1]))
        crl.add_revoked(revoked)
    
    with open("test.crl","wb") as f:
        f.write(crl.export(public_key,private_key,crypto.FILETYPE_PEM,days=30,digest=b'sha256'))

    return ""

@mod_certificates.route("/restore",methods=["POST"])
@process_request
def restore_certificates():

    # Getting JSON data
    data = request.get_json()

    # Getting the specified certificates
    cert = Certificate.query.get(data['id'])
    if not cert:
        abort(config.http_notfound,{"message":config.error_cert_notfound})

    # Checking certificate current status
    if cert.status != config.STATUS_PAUSED:
        abort(config.http_notfound,{"message":config.error_cert_status})

    # Changing the status back to Active
    cert.status = 1
    cert.reason_revoke = ""
    cert.code_revoke = -1
    cert.date_revoke = None
    db_session.commit()

    return jsonify(message=config.msg_cert_restored),config.http_ok

#### Deleting certificates
@mod_certificates.route("/delete",methods=["DELETE"])
@process_request
def delete_certificates():
    
    # Getting JSON data
    data = request.get_json()

    # Getting the list of selected templates
    certs = Certificate.query.filter(Certificate.id.in_(data))
    for cert in certs:
        db_session.delete(cert)
    db_session.commit()
    return jsonify(message=config.msg_certs_deleted),config.http_ok