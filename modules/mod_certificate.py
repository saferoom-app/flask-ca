# Import section
from flask import Blueprint, jsonify,abort,request,render_template

# Initializing the blueprint
mod_certificate = Blueprint("mod_certificate",__name__)

# Routes
@mod_certificate.route("/",methods=["GET","POST"])
def list_ca():

    # IF GET method, then return the HTML page
    if request.method == "GET":
    	certificates = []
    	certificates.append({"name":"Test 2"})
    	certificates.append({"name":"Test 2"})
    	certificates.append({"name":"Test 2"})
    	certificates.append({"name":"Test 2"})
    	certificates.append({"name":"Test 2"})
    	certificates.append({"name":"Test 2"})
        abort(400,{"message":"There was a problem handling HTTP request"})
        return jsonify(certificates)

    # if POST, we are listing the created certificates
    return ""