var caid = 0;
$(document).ready(function(){
	// Listing the Certificate Authorities
	list_cas();	
});

function list_cas(){
    
    filter = {search:$("#txtSearch").val()}

	$("#caList").html(TPL_LOADING);
	CreateAJAX("/ca/list","POST","json",JSON.stringify(filter))
	.done(function(response){
		$.get("/static/templates/ca.list.html",function(template){
			caList = Handlebars.compile(template);
			$("#caList").html(caList(response));
		});
	})
	.fail(function(xhr){$("#caList").html("");handle_error(xhr);});
}

$(document).on("click","button",buttonHandler);
$(document).on("change","select",changeHandler);
$(document).on("blur","input,select",blurHandler);

function buttonHandler(event){
	var id = event.currentTarget.id;
	switch (id){
		case "btnCreate":$(".alert").hide();show_modal("createca","Create new CA",true,true);break;
		case "btnApply":
			if ($("#txtOP").val() == "generatecrl"){
				generate_crl($("#txtPassword").val());

			}
			else{create_ca();}

			break;
		case "btnFilter":list_cas();break;
		case "btnDownloadCA":
			download_ca($(event.currentTarget).attr("data"))
			break;
		case "btnGenerateCRL":
			caid = parseInt($(event.currentTarget).attr("data"));
			show_modal("password","Private key password",true,true,false);
			break;
		case "btnDownloadCRL":
			caid = parseInt($(event.currentTarget).attr("data"));
			show_modal("crls/"+$(event.currentTarget).attr("data"),"List of generated CRLs",false,true,false)
			break;
	}
}

function changeHandler(event){
	var id = event.currentTarget.id;
	switch (id){
		case "selectCRL":
			if ($("#selectCRL option:selected").val() == "1"){
				$("#txtFull").val(get_current_url()+"/ca/<ca_id>/crl/full");
				$("#txtFreshest").val(get_current_url()+"/ca/<ca_id>/crl/delta");
			}
			else{$("#txtFull").val("");$("#txtFreshest").val("");}			
			break;
		case "selectOCSP":
			if ($("#selectOCSP option:selected").val() == "1"){
				$("#txtOCSP").val(get_current_url()+"/ca/<ca_id>/aia/ocsp");
			}
			else{$("#txtOCSP").val("");}			
			break;
		case "selectIssuers":
			if ($("#selectIssuers option:selected").val() == "1"){
				$("#txtIssuers").val(get_current_url()+"/ca/<ca_id>/aia/issuers");
			}
			else{$("#txtIssuers").val("");}
		case "selectType":
			$("#selectRoot").prop("disabled",($("#selectType option:selected").val() == "0"));
			$("#txtRootPass").prop("disabled",($("#selectType option:selected").val() == "0"));
			break;
	}
}


function blurHandler(event){
	var id = event.currentTarget.id;
	switch (id){
		case "txtName": // we need to append this value as CN to Subject DN
			$("#txtSubject").val(append_value("CN",$("#txtName").val()));
			break;
		case "txtO":
			$("#txtSubject").val(append_value("O",$("#txtO").val()));
			break;
		case "txtOU":
			$("#txtSubject").val(append_value("OU",$("#txtOU").val()));
			break;
		case "txt_C":
			$("#txtSubject").val(append_value("C",$("#txt_C option:selected").val()));
			break;
		case "txtST":
			$("#txtSubject").val(append_value("ST",$("#txtST").val()));
			break;
		case "txtL":
			$("#txtSubject").val(append_value("L",$("#txtL").val()));
			break;
	}
}

function append_value(field,value){

	// Getting subject DN
	var subject_dn = []
	var contains = false;
	
	// Searching if the value has been already specified
	if ($("#txtSubject").val() != ""){
        subject_dn = $("#txtSubject").val().split(",");
		for (i=0;i<subject_dn.length;i++){
			if (subject_dn[i].split("=")[0].trim() == field){
				if (value == ""){subject_dn.splice(i,1);}
				else{subject_dn[i] = field+"="+value;}
				contains = true
			}		
		}
		if (!contains){subject_dn.push(field+"="+value);}
	}
	else{
		subject_dn.push(field+"="+value);		
	}
	return subject_dn.join(",");

}

function create_ca(){
	// Checking values
	var txtName = $("#txtName");
	var txtPassword = $("#txtPassword");

	if (txtName.val() == ""){txtName.focus();
		show_alert(TYPE_ERROR,"Certificate Authority name is mandatory");
		return;
	}
	if (txtPassword.val() == ""){txtPassword.focus();
		show_alert(TYPE_ERROR,"You must specify password to protect your private key. Go to tab [Security] and specify password");
		return;
	}

	// Initializing CA
	show_alert(TYPE_SUCCESS,"Creating new Certificate Authority. Please wait ....");
	var ca = CertificateAuthority.init($(document));
	ca.create();
}
function download_ca(id){
	location.href = "/ca/"+id+"/crt"
}
function generate_crl(password){
	show_alert(TYPE_SUCCESS,"Generating new CRL. Please wait ....");
	CreateAJAX("/ca/"+caid+"/crl/generate","POST","json",JSON.stringify({pass:password}))
	.done(function(response){showToast("success",response.message,true);})
	.fail(function(xhr){handle_error(xhr,true);})
	.always(function(jqXHR, textStatus){hide_modal();});
}


$( document ).ajaxComplete(function(event,xhr,settings) {
	if (xhr.status == 200 || xhr.status == 201){
  		switch (settings.url){
  			case "/ca/create":$("#modalDialog").modal("hide");list_cas();break;  		
  		}
  	}
});

$(document).on("click","tr#crlRow",function(){
	location.href = "/ca/crl/get/"+$(this).attr("data");
});


/*$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
  //if ($(e.target).html() == "Topology"){build_tree(); }
})*/