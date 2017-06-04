# Import section
from flask import Blueprint, jsonify,abort,request,render_template
from app.core.models import Template
from app.core.decorators import process_request
from app.core.database import db_session
import app.config.caconfig as config

# Initializing the blueprint
mod_template = Blueprint("mod_template",__name__,url_prefix='/tpls')

# Routes
@mod_template.route("/",methods=["GET","POST"])
def index_templates():
    return render_template("mod_templates/index.html",active="tpl")

@mod_template.route("/view/<string:tplid>/",methods=["GET"])
def view_template(tplid):
    return render_template("mod_templates/view.html",active="tpl",tpl_id=tplid)


@mod_template.route("/list",methods=["GET"])
def list_templates():

    result = Template.query.all()
    templates = []
    for template in result:
    	templates.append({"id":template.id,"name":template.name,"description":template.dscr})
    return jsonify(templates=templates)

@mod_template.route("/create",methods=["POST"])
@process_request
def create_template():
    
    # Getting JSON data
    data = request.get_json()
    
    # Creating new Template
    template = Template(name=data['name'],dscr=data['dscr'])
    template.set_extensions(data['extensions'])
    
    # Adding template to the database
    db_session.add(template)
    db_session.commit()

    return jsonify(message=config.msg_tpl_created,template={"id":template.id,"name":template.name}),config.http_created

@mod_template.route("/delete",methods=["DELETE"])
@process_request
def delete_template():
    
    # Getting JSON data
    data = request.get_json()

    # Getting the list of selected templates
    tpls = Template.query.filter(Template.id.in_(data))
    for tpl in tpls:
        db_session.delete(tpl)
    db_session.commit()
    return jsonify(message=config.msg_tpls_deleted),config.http_ok

@mod_template.route("/get/<string:tplid>")
def get_template(tplid,format="json"):

    # Getting the template
    result = Template.query.filter_by(id=tplid).first()
    if not result:
        abort(config.http_notfound,{"message":config.error_template_notfound})
    return jsonify(template=result.as_dict(),key_usages=config.key_usages,ext_key_usages=config.ext_key_usages)

@mod_template.route("/update",methods=["POST"])
@process_request
def update_template():

    # Getting JSON
    data = request.get_json()
    
    # Getting template from the database
    template = Template.query.filter_by(id=data['id']).first()
    if not template:
        abort(config.http_notfound,{"message":config.error_template_notfound})
    
    # Updating template
    template.name = data['name']
    template.dscr = data['dscr']
    template.set_extensions(data['extensions'])
    db_session.commit()
    return jsonify(message=config.msg_tpl_updated),config.http_ok
