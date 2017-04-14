$(document).ready(function(){
	$("[rel=tooltip]").tooltip({ placement: 'right'});
});

$(document).on("click","button",buttonHandler);
$(document).on("change","select",changeHandler);
function buttonHandler(event){
	var id = event.currentTarget.id;
	switch (id){
		case "btnAdd":
			show_modal("adduser","Add new user",true,true,false);
			break;
		case "btnApply":
			do_operation();
			break;
		case "btnCancel":
			history.go(-1);
			break;
		case "btnGenerate":
			generate_certificates();
			break;
		case "btnSelect":
			show_modal("listusers","Select users",true,true,true);
			break;
	}
}

function do_operation(){
    var op = $("#modalDialog").find("#txtOp").val();
    switch (op){
        case "select":select_users();break;
        default:add_user();break;
    }
}

function changeHandler(event){
	var id = event.currentTarget.id;
	switch (id){
		case "txtCA":
			show_alert(TYPE_SUCCESS,"Loading the Certificate Authority information");
			if ($("#"+id+" option:selected").val() != ""){
				CreateAJAX("/ca/get/"+$("#"+id+" option:selected").val(),"GET","json",{})
				.done(function(response){
					var timeStamp = Math.floor(Date.now() / 1000);
					$("#txtValid").val(Math.floor((response.expires - timeStamp)/(60*60*24*30)));
					set_maximum_validity();
				})
				.fail(function(xhr){

				})
				.always(function(){
					$("div#panelAlert").hide();
				});
			}
			break;
	}
}

function append_users(users){

	// First, clearing the row
	if ($("#tblUsers tbody").find("tr#userRow").length == 0){
		$("#tblUsers tbody").find("tr#emptyRow").remove();
	}

	user_row = "<tr data='::id::' id='userRow'><td><span class=\"glyphicon glyphicon-remove removeIcon\" aria-hidden=\"true\"></span></td><td id='userName'>::name::</td><td id='userEmail'>::email::</td><td id='userDN'>::subject::</td><td id='userValid'><input type='password' class=\"form-control\" id='userPass'/></td><td id='userValid'><input type='number' class=\"form-control\" value='1' max='120' min='1' id='userValid'/></td></tr>";
	for (i=0;i<users.length;i++){
		$("#tblUsers tbody").append(
			user_row.replace("::id::",users[i].id).replace("::name::",users[i].name)
				.replace("::email::",users[i].email)
				.replace("::subject::",users[i].subject)
        	);
        }
    
    $("#modalDialog").modal("hide");
}
function select_users(){
	users = new Array();
	$("#tblSelectUsers tbody").find("input[id!='selectAll']:checked").each(function(){
    	users.push({
        	id:parseInt(this.id),
        	name:$(this).parent().parent().find("td#userName").html(),
        	email:$(this).parent().parent().find("td#userEmail").html(),
        	subject:$(this).parent().parent().find("td#userDN").html(),
    	});
    });

    append_users(users)
    
}
function generate_certificates(){
    
    // First, we check that at least one user is selected
    if ($("#tblUsers tbody").find("tr#userRow").length == 0){
    	show_alert(TYPE_ERROR,"Please select at least one user");
    	scrollTop();
    	return;
    }

    // Checking that template has been selected
    if ($("#txtCA option:selected").val() == ""){
    	$("#txtCA").focus();
    	show_alert(TYPE_ERROR,"Please select Certificate Authority to issue certificate(s)");
    	scrollTop();
    	return;
    }

    // Checking that template has been selected
    if ($("#txtTPL option:selected").val() == ""){
    	$("#txtTPL").focus();
    	show_alert(TYPE_ERROR,"Please select template to generate certificate(s)");
    	scrollTop();
    	return;
    }

    // Initialize the array of certificates to be generated
    certificates = new Array();

    // Listing the users and add to Array
    $("#tblUsers tbody").find("tr#userRow").each(function(){
    	certificates.push({
    		uid:$(this).attr("data"),
    		ca: parseInt($("select#txtCA option:selected").val()),
    		tpl: parseInt($("select#txtTPL option:selected").val()),
    		pass:$(this).find("input#userPass").val(),
    		valid: parseInt($(this).find("input#userValid").val())
    	})
    });
    
    // Generate SID for tracking status
    sid = generate_guid();
    var total = certificates.length;
	set_progress("Initializing <img style='margin-left:10px' src='/static/images/2.gif'/>",0,total);
    
    // Displaying modal windows
	$("#modalProgress").modal("show");
    var interval = setInterval(function(){get_status(sid)},3000);

    // Sending request
    CreateAJAX("/certificates/generate","POST","json",JSON.stringify({sid:sid,certificates:certificates,pass:$("#txtPass").val()}))
    .done(function(response){
    	clearInterval(interval);set_progress("Finished",total,total)
		$("button#btnClose").prop("disabled",false);
    	
    })
    .fail(function(xhr){
    	clearInterval(interval);set_progress(xhr.responseText,0,0)
		$("button#btnClose").prop("disabled",false);
    });

}
$(document).on("click",".removeIcon",function(){$(this).closest('tr').remove();
	if ($("#tblUsers tbody").find("tr#userRow").length == 0){
		$("#tblUsers tbody").html("<tr id=\"emptyRow\"><td colspan=\"10\"><div class=\"row\"><div class=\"col-md-12 greyedText\" style=\"text-align:center\">-- No users added yet -- </div></div></td></tr>");
	}
});

function set_maximum_validity(){
	var number;
	$("#tblUsers tbody").find("tr#userRow").each(function(){
		number = $(this).find("input[type=number]");
		number.prop("max",parseInt($("#txtValid").val()));
		if (number.val() > parseInt($("#txtValid").val())){
			number.val(parseInt($("#txtValid").val()));
		}
	});
}

$( document ).ajaxComplete(function(event,xhr,settings) {
  	switch (settings.url){
  		case "/status":list_templates();break;  		
  	}
});