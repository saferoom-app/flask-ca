# Import flask and template operators
from config.config import DevelopmentConfig
import os
from flask import Flask, render_template,jsonify,redirect,url_for,send_from_directory,request
from flask_sqlalchemy import SQLAlchemy
from core.functions import get_status
from models import db

# Define the WSGI application object
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
db.init_app(app)

# Import a module / component using its blueprint handler variable (mod_auth)
from mod_ca.controllers import mod_ca
from mod_tpl.controllers import mod_template
from mod_dialog.controllers import mod_modal
from mod_certificates.controllers import mod_certificates
from mod_users.controllers import mod_users

# Registering Blueprints
app.register_blueprint(mod_ca)
app.register_blueprint(mod_template)
app.register_blueprint(mod_modal)
app.register_blueprint(mod_certificates)
app.register_blueprint(mod_users)

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.teardown_appcontext
def shutdown_session(exception=None):
    pass

@app.route("/",methods=["GET"])
def index_page():
	return redirect(url_for("mod_ca.ca_index_page"))

@app.route("/start",methods=["GET"])
def start_app():
    return render_template("start.html",pageTitle="Saferoom CA :: Getting started")

@app.route("/status/<string:sid>")
def get_operation_status(sid):
    return jsonify(get_status(sid,caconfig.path_status))

@app.route("/favicon.ico")
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))



############################################################
# 			          Custom handlers
############################################################

@app.errorhandler(400)
def custom_400(error):
    return jsonify({'message': error.description['message']}),400

@app.errorhandler(401)
def custom_401(error):
    return jsonify({'message': error.description['message']}),401

@app.errorhandler(404)
def custom_404(error):
    return jsonify({'message': error.description['message']}),404

@app.errorhandler(403)
def custom_403(error):
    return jsonify({'message': error.description['message']}),403

@app.errorhandler(500)
def custom_500(error):
	return jsonify({'message': "Internal server error"}),500

if __name__ == '__main__':
    app.run()
