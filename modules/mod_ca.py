# Import section
from flask import Blueprint, abort,request,render_template,jsonify
from core.models import CertificateAuthority, Key
from core.database import db_session
import config,json,datetime
from OpenSSL import crypto
from dateutil.relativedelta import relativedelta

# Initializing the blueprint
mod_ca = Blueprint("mod_ca",__name__)

# Routes
@mod_ca.route("/create",methods=["POST"])
def create_ca():
    '''
		Function is used to create new CA (Root or Subordinate). If we're creating the Subordinate CA, we need to specify the "root_ca". By default it's None
    '''
    print "asdasdasdasdsadasd"
    # Parsing request
    data = request.get_json()    

    # Creating new CA
    ca = CertificateAuthority(name=data['name'],subject_dn=json.dumps(data['subject_dn']))
    
    # If Root CA is specified we need to get its key
    root_key = None
    root_cert = None
    if "rootca" in data:
    	key = Key.query.get(data['rootca'])
    	if not key:
    		abort(config.http_not_found,{"message":"Root CA not found"})

    	# Getting CA key
    	root_key = crypto.load_privatekey(crypto.FILETYPE_PEM,key.private,passphrase="testtest")
    	root_cert = crypto.load_certificate(crypto.FILETYPE_PEM,key.public) 	    	

    	# Setting the Root ca
    	ca.set_root(data['rootca'])
    
    # Creating a pair of keys
    key = Key()
    key.generate_private_key(data['pass'],data['keylen'])
    key.generate_public_key(data['subject_dn'],data['months'],root_key,root_cert)
    key.expires_in = datetime.datetime.now() + relativedelta(months=data['months'])

    with open("intermediate.crt","w") as f:
    	f.write(key.public)
        

    # Adding to database
    ca.keys.append(key)
    db_session.add(ca)
    db_session.add(key)
    db_session.commit()

    return jsonify(status=config.http_created),config.http_created