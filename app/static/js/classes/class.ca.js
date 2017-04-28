/*
	
	Class defines the Certificate Authority and its operations:

	create() = function is used to create the CA
	
	update() = function used to update the existing CA
	
	init(doc)   = function used to initialize the CA from Web page elements. 
		>> doc = jQuery document object
	
	delete(id) = static function used to delete Certificate Authority. 
		>> id = Certificate Authority ID

*/

class CertificateAuthority{
	constructor(){
		this.id = "",
		this.name = "",
		this.dscr = "",
		this.pass = "",
		this.subjectDN = {},
		this.keylen = 1024,
		this.hash = "sha1",
		this.valid = 1
		this.extensions = {
			crl:"",			
			ocsp:"",
			issuers:""
		},
		this.root_ca = {
			ca_id: 0,
			pass:""
		}
	}

	static init(doc){
		var ca = new CertificateAuthority()
		ca.name = doc.find("#txtName").val();
		ca.dscr = doc.find("textarea#txtDscr").val();
		ca.pass = doc.find("#txtPassword").val();
		ca.keylen = parseInt(doc.find("#txtKeylen option:selected").val());
		ca.valid = parseInt(doc.find("#txtValid").val());
		ca.hash = doc.find("#txtHash option:selected").val();

		// Generating Subject DN
		ca.subjectDN["CN"] = ca.name;
		if (doc.find("#selectCountry option:selected").val() != ""){
			ca.subjectDN["C"] = doc.find("#selectCountry option:selected").val();
		}
		if (doc.find("#txtO").val() != ""){
			ca.subjectDN["O"] = doc.find("#txtO").val();
		}
		if (doc.find("#txtOU").val() != ""){
			ca.subjectDN["OU"] = doc.find("#txtOU").val();
		}
		if (doc.find("#txtST").val() != ""){
			ca.subjectDN["ST"] = doc.find("#txtST").val();
		}
		if (doc.find("#txtL").val() != ""){
			ca.subjectDN["L"] = doc.find("#txtL").val();
		}
        
        // Extensions
        ca.extensions.crl = (doc.find("#selectCRL option:selected").val() == "0" ? "" : get_current_url()+"/ca/<ca_id>/crl/full");
        ca.extensions.ocsp = (doc.find("#selectOCSP option:selected").val() == "0" ? "" : get_current_url()+"/ca/<ca_id>/ocsp");
        ca.extensions.issuers = (doc.find("#selectIssuers option:selected").val() == "0" ? "" : get_current_url()+"/ca/<ca_id>/issuers");

        // Setting Root CA
        if (doc.find("#selectType option:selected").val() == "1"){
        	ca.root_ca.ca_id = parseInt(doc.find("#selectRoot option:selected").val());
        	ca.root_ca.pass = doc.find("#txtRootPass").val();

        }
        return ca;
	}

	create(){
		CreateAJAX("/ca/create","POST","json",JSON.stringify(this))
		.done(function(response){showToast("success",response.message,true);})
		.fail(function(xhr){handle_error(xhr,true);});
	}

	static delete(id,pass){
		CreateAJAX("/ca/"+id+"/delete","DELETE","json",JSON.stringify({pass:pass}))
		.done(function(response){showToast("success",response.message,true);})
		.fail(function(xhr){handle_error(xhr,true);})
		.always(function(xhr,status){hide_alert();});
	}
}	