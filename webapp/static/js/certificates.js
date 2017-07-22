var current_page = 1
$(document).ready(function(){
    certs = new Array();
    list_certificates();
});

function list_certificates(){
    
    var statuses = $("select#status").val().map(Number);
    statuses.splice(0,1);
    var cas = $("select#ca").val().map(Number);
    cas.splice(0,1);

    filter = {
    	search:$("input#txtSearch").val(),
    	ca:cas,
    	status:statuses,
        page:current_page
    }
    CreateAJAX("/certificates/list","POST","json",JSON.stringify(filter))
    .done(function(response){
    	$.get("/static/templates/certificates.list.html",function(template){
            certList = Handlebars.compile(template);
            $("#certificateList").html(certList(response));
            $("li#page_"+current_page).addClass("active");
        });
    })
    .fail(function(xhr){

    });
}

$(document).on("click","button",buttonHandler);

function buttonHandler(event){
	var id = event.currentTarget.id;
	switch (id){
        case "btnFilter":
            list_certificates();
            break;
        case "btnGenerate":
            location.href = "/certificates/create";
            break;
        case "btnRevoke":
            if (window.confirm("Are you sure that you want to revoke selected certificate(s)?")){
                if ($("input[id!='selectAll']:checked").length == 0){
                    show_alert(TYPE_ERROR,"Select al least one certificate to revoke");
                    return;
                }
                show_modal("revoke","Revocation reason",true,true,false);}
            break;
        case "btnApply":
            revoke_certificates();
            break;
        case "btnDownloadPub":
            location.href = "/certificates/download/public/"+event.currentTarget.getAttribute("data");
            break;
        case "btnDownloadPFX":
            location.href = "/certificates/download/"+event.currentTarget.getAttribute("data");
            break;

        case "btnRestore":
            if (window.confirm("Are you sure that you want to restore this certificate?")){
                restore_certificates(event.currentTarget.getAttribute("data"))
            }
            break;
        case "btnDelete":
            if ($("input[id!='selectAll']:checked").length == 0){
                show_alert(TYPE_ERROR,"Select at least one certificate to delete");
                return;
            }
            if (window.confirm("Are you sure that you want to delete selected certificate(s)?")){
                delete_certificates();
            }
            
            break;
    }
}

function revoke_certificates(){
    
    certs = new Array();
    $("input[id!='selectAll']:checked").each(function(){
        certs.push(parseInt(this.id));
    });
    
    request = {
        certs:certs,
        reason: parseInt($("#txtReason option:selected").val()),
        comment: $("#txtComment").val()
    }

    CreateAJAX("/certificates/revoke","POST","json",JSON.stringify(request))
    .done(function(response){
        hide_modal();showToast("success",response.message,true);
        list_certificates();})
    .fail(function(xhr){handle_error(xhr,true);});
}
$(document).on("click","ul.pagination li",function(){
    current_page = parseInt($(this).find("a").html());
    list_certificates()
    return false;
});
$(document).on("click","td a",function(event){
    var id = $(this).parent().parent().find("input[type='checkbox']").prop("id");
    show_modal("certificates/"+id,"Certificate Info",false,true,true);
    event.stopPropagation();
});
function restore_certificates(id){
    CreateAJAX("/certificates/restore","POST","json",JSON.stringify({id:id}))
    .done(function(response){showToast("success",response.message,true);list_certificates();})
    .fail(function(xhr){handle_error(xhr,true);})
}
function delete_certificates(){
    certs = new Array();
    $("input[id!='selectAll']:checked").each(function(){certs.push(this.id);});
    CreateAJAX("/certificates/delete","DELETE","json",JSON.stringify(certs))
        .done(function(response){list_certificates();showToast("success",response.message,true);})
        .fail(function(xhr){handle_error(xhr);});
 }
