# Import section
from flask import Blueprint, jsonify,abort,request,render_template
import app.config.caconfig as config
from app.core.models import CertificateAuthority, Template, User, CRL, Certificate

# Initializing the blueprint
mod_modal = Blueprint("mod_modal",__name__,url_prefix='/modal')

## Route 1. Create Template dialog
@mod_modal.route("/createtpl",methods=["GET"])
def dialog_createtpl():
	return render_template("dialogs/dialog.create_template.html",key_usages=config.key_usages,\
		                   ext_key_usages=config.ext_key_usages)

@mod_modal.route("/createca",methods=["GET"])
def dialog_createca():
    
    # Getting a list of created Certificate Authorities
    result = CertificateAuthority.query.all()
    cas = [{"id":ca.id,"name":ca.name} for ca in result]

    return render_template("dialogs/dialog.create_ca.html",cas=cas)

@mod_modal.route("/adduser",methods=["GET"])
def dialog_adduser():
	
    # Sending HTML template
    return render_template("dialogs/dialog.add_user.html",user={"subject":{},"id":""},op="create")

@mod_modal.route("/revoke",methods=["GET"])
def revoke_cert():
	return render_template("dialogs/dialog.revoke.html",reasons=config.reasons)

@mod_modal.route("/getuser/<string:id>",methods=["GET"])
def get_user(id):
    
    # Getting user
    result = User.query.get(id)
    if not result:
        abort(config.http_notfound,{"message":config.error_user_notfound})

    # Sending HTML template

    return render_template("dialogs/dialog.add_user.html",user=result.as_dict(),op="update")

@mod_modal.route("/listusers",methods=["GET"])
def list_users():

    # Getting user
    result = User.query.all()

    # Processing the result
    users = []
    for user in result:
        users.append({"id":user.id,"name":user.name,"email":user.email,"subject":user.subject})

    # Sending response
    return render_template("dialogs/dialog.select_users.html",users=users,op="select")

@mod_modal.route("/password",methods=["GET"])
def prompt_password():
    return render_template("dialogs/dialog.password.html",op="generatecrl")

@mod_modal.route("/crls/<string:caid>")
def list_crls(caid):
    # Getting a list of CRLs
    crls = []
    result = CRL.query.filter_by(ca=caid).all()
    for crl in result:
        crls.append({"id":crl.id,"created":crl.created})
    return render_template("dialogs/dialog.crls.html",op="crl",crls=crls)

@mod_modal.route("/certificates/<string:cid>")
def get_certificate(cid):
    
    # Getting a certificate
    cert = Certificate.query.get(cid)
    if not cert:
        abort(config.http_notfound,{"message":config.error_cert_notfound})

    # Sending response
    return render_template("dialogs/dialog.certificate.html",certificate=cert)

