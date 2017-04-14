/*
	
	Class defines the Certificate template and its operations:

	create() = function is used to create the template
	
	update() = function used to update the existing template
	
	init(doc)   = function used to initialize the template from Web page elements. 
		>> doc = jQuery document object
	
	delete(ids) = static function used to delete a list of templates. 
		>> ids = array of template IDs to be deleted 

*/

class Template{
	constructor(){
		this.id = "";
		this.name = "";
		this.dscr = "";
		this.extensions = {
			altname:"",
			ku:[],
			sku:[],
			policies:[],
			crl:{
				inherit:"",
				full:"",
				freshest:""
			},
			aia:{
				inherit:"",
				ocsp:"",
				issuers:""
			},
			keylen:0
		}
	}

	create(){
		// Sending request to server
		CreateAJAX("/tpls/create","POST","json",JSON.stringify(this))
		.done(function(response){showToast("success",response.message,true);})
		.fail(function(xhr){handle_error(xhr,true);});
	}

	update(){
		// Sending request to server
		CreateAJAX("/tpls/update","POST","json",JSON.stringify(this))
		.done(function(response){showToast("success",response.message,true);})
		.fail(function(xhr){handle_error(xhr,true);});	
	}

	static init(doc){
		var template = new Template();
		var policies = []
		template.name = doc.find("input#txtName").val();
		template.dscr = doc.find("textarea#txtDscr").val();
		template.extensions.altname = doc.find("input#txtAltName").val();
	    template.extensions.ku = doc.find("select#ku").val();
	    template.extensions.sku = doc.find("select#sku").val();
	    template.extensions.crl.inherit = parseInt(doc.find("#txtCRLInh option:selected").val());
	    template.extensions.crl.full = doc.find("#txtCRL").val();
	    template.extensions.crl.freshest = doc.find("#txtFreshest").val();
	    template.extensions.aia.inherit = parseInt(doc.find("#txtAIAInh option:selected").val());
	    template.extensions.aia.ocsp = doc.find("#txtOCSP").val();
	    template.extensions.aia.issuers = doc.find("#txtIssuers").val();
	    doc.find("#tbodyPolicies tr").each(function(){console.log($(this).html());policies.push($(this).find("td#tdPolicy").html());});
	    template.extensions.keylen = parseInt(doc.find("#txtKeylen option:selected").val());
	    template.extensions.policies = policies;	    
	    return template;
	}

	static delete(ids){
		CreateAJAX("/tpls/delete","DELETE","json",JSON.stringify(ids))
		.done(function(response){showToast("success",response.message,true);})
		.fail(function(xhr){handle_error(xhr);});
	}
}