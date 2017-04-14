$(document).ready(function(){
    // Getting CA
    get_ca($("#ca_id").val());
});

$(document).on("click","span#btnDownload",function(){
	var id = $(this).parent().parent().prop("id");
	location.href = "/ca/crl/get/"+id;
});
$(document).on("click","span#btnRemove",function(){
	if (window.confirm("Are you sure that you want to delete specified CRL?")){
		row = $(this).parent().parent();
		var id = row.prop("id");
		CreateAJAX("/ca/crl/delete/"+id,"DELETE","json",JSON.stringify({}))
		.done(function(response){showToast("success",response.message,true);row.remove();})
		.fail(function(xhr){handle_error(xhr,true);})
		.always(function(xhr,status){});
	}
});

function get_ca(id){
	$("#ca_content").html("<img src=\"/static/images/89.gif\"/>");
	CreateAJAX("/ca/get/"+id,"GET","json",{})
	.done(function(response){        
        response.ca.expires = formatDate(new Date(response.ca.expires*1000))        
		$.get("/static/templates/ca.view.html",function(template){
			tpl = Handlebars.compile(template);
			$("#ca_content").html(tpl(response));		
		});
	})
	.fail(function(xhr){$("#ca_content").html(xhr.responseText);})
}