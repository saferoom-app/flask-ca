# Import section
from flask import Flask, jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
from core.database import db_session,init_db
from OpenSSL import crypto, SSL
from core.models import Key, CertificateAuthority, Certificate, Template
import json,datetime,config,hashlib,uuid
from dateutil.relativedelta import relativedelta
from core.functions import force_bytes


# Importing blueprints
from modules.mod_ca import mod_ca
from modules.mod_certificate import mod_certificate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'

# Registering blueprints
app.register_blueprint(mod_ca,url_prefix="/ca")
app.register_blueprint(mod_certificate,url_prefix="/certificates")



@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/init")
def init():
    init_db()
    
    # Initializing the predefined templates
    tpl = Template("Server Authentication certificate","This is the template to create Server Authentication certificates")
    extensions = []
    extensions.append({"name":"bc","crit":True,"value": "pathlen:0"})
    extensions.append({"name":"ku","crit":True,"value": "%s,%s,%s" % (config.key_usage['digsign'],config.key_usage['keyenc'],config.key_usage['keyag'])})
    extensions.append({"name":"eku","crit":True,"value": "%s" % config.ext_key_usage['sa']})
    tpl.extensions = json.dumps(extensions)
    db_session.add(tpl)
    db_session.commit()
    return ""

@app.route("/demo")
def demo():
    
    
    print tpl
    return ""

    

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/issue/<string:id>")
def issue_cert(id):

    # Getting the Certificate Authority Information
    ca = CertificateAuthority.query.get(id)
    if not ca:
        return "Not found"

    # Getting the template
    tpl = Template.query.get(1)

    # Generating certificate
    post = '{"CN":"Alexey Zelenkin","C":"US","OU":"Saferoom","O":"Saferoom"}'
    data = json.loads(post)
    certificate = Certificate.generate(ca.id,data,12,extensions=json.loads(tpl.extensions))
    certificate.authority = ca
    db_session.add(certificate)
    db_session.commit()



    return ""

@app.route("/revoke/<string:cid>")
def revoke_certificate(cid):

    # Getting the certificate
    certificate = Certificate.query.get(cid)

    # Getting Certificate Authority
    key = Key.query.filter_by(ca=certificate.ca).first()
    if not key:
    	abort(404,{"message":"Certificate Authority key not found"})

    # Getting private and public keys
    private_key = crypto.load_privatekey(crypto.FILETYPE_PEM,key.private,passphrase="testtest")
    public_key = crypto.load_certificate(crypto.FILETYPE_PEM,key.public)
    
    with open("test.crl","r") as f:
        crl = crypto.load_crl(crypto.FILETYPE_PEM,f.read())
    revoked = crypto.Revoked()
    revoked.set_serial(force_bytes(certificate.serial))
    revoked.set_reason(None)
    crl.add_revoked(revoked)
    
    # Dump CRL into file
    with open("test.crl","w") as f:
        f.write(crl.export(public_key,private_key,crypto.FILETYPE_PEM,1,"sha256"))


############################################################
# 			          Custom handlers
############################################################

@app.errorhandler(400)
def custom_400(error):
    return jsonify({'message': error.description['message']}),400

@app.errorhandler(403)
def custom_403(error):
    return jsonify({'message': error.description['message']}),403

@app.errorhandler(500)
def custom_500(error):
	return jsonify({'message': "Internal server error"}),500


if __name__ == '__main__':
    app.run(debug=True)