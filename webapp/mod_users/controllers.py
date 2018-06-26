# Import section
from flask import Blueprint, jsonify,abort,request,render_template
from webapp.models import db,User
from webapp.core.decorators import process_request
import webapp.config.caconfig as config

# Initializing the blueprint
mod_users = Blueprint("mod_users",__name__,url_prefix='/users')

# Routes
@mod_users.route("/",methods=["GET"])
def index_users():
	return render_template("mod_users/index.html",active="users")

@mod_users.route("/list",methods=["POST"])
def list_users():

	# Getting a list of users
	users = []
	result = User.query.all()
	for user in result:
		users.append({"id":user.id,"name":user.name,"email":user.email,"subject":user.subject})
	return jsonify(users=users)

@mod_users.route("/create",methods=["POST"])
@process_request
def create_user():

	# Getting JSON data
	data = request.get_json()

	# Checking that all data has been submitted
	if "name" not in data or "email" not in data or "subject" not in data:
		abort(config.http_bad_request,{"message":config.error_bad_request})

	# Creating new user
	user = User(data['name'])
	user.email = data['email']
	user.subject = data['subject']
	db.session.add(user)
	db.session.commit()

	# Sending response
	return jsonify(message=config.msg_user_created,user={"id":user.id,"name":user.name}),config.http_created

@mod_users.route("/update",methods=["POST"])
@process_request
def update_user():

	# Getting JSON data
    data = request.get_json()
    
    # Checking that all data has been submitted
    if "name" not in data or "email" not in data or "subject" not in data:
        abort(config.http_bad_request,{"message":config.error_bad_request})

    # Getting the user
    user = User.query.get(data['id'])
    if not user:
        abort(config.http_notfound,{"message":config.error_user_notfound})
    user.name = data['name']
    user.email = data['email']
    user.subject = data['subject']
    db.session.commit()

    # Sending response
    return jsonify(message=config.msg_user_updated),config.http_ok

@mod_users.route("/delete",methods=["DELETE"])
@process_request
def delete_users():

	# Getting JSON data
    data = request.get_json()
        
    # Getting the list of selected templates
    users = User.query.filter(User.id.in_(data))
    for user in users:
        db.session.delete(user)
    db.session.commit()
    return jsonify(message=config.msg_users_deleted),config.http_ok
