TYPE_INFO = 0
TYPE_ERROR = 1
TYPE_WARN = 2
TYPE_SUCCESS = 3

TPL_LOADING = "<img src=\"/static/images/89.gif\"/>";

function showToast(type,message,top){
	if (top == true){position = "toast-top-right";}
	else{position = "toast-bottom-center";}
	toastr.options = {
		"closeButton": false,
		"debug": false,"newestOnTop": false,"progressBar": false,
		"positionClass": position,"preventDuplicates": false,
		"onclick": null,"showDuration": "300","hideDuration": "1000",
		"timeOut": "6000","extendedTimeOut": "1000","showEasing": "swing",
		"hideEasing": "linear","showMethod": "fadeIn","hideMethod": "fadeOut"
	}

	switch (type)
	{
		case "success": // success
			toastr['success'](message);
			break;
		case "warn": //warning
			toastr['warning'](message);
			break;
		case "danger": // error
			toastr['error'](message);
	}
}

function CreateAJAX(url,requestType,dataType,data){
    
    contentType = ""
    switch (requestType)
    {
    	case "GET":
    		contentType = "text/html";
    		break;
    	case "POST":
        case "DELETE":
    		if (dataType == "json"){contentType = "application/json; charset=utf-8";}
    		else{contentType = "application/x-www-form-urlencoded; charset=utf-8";}
    		break;
    }

	return $.ajax({
     	// The URL for the request
    	url: url, 
    	data: data,
    	type: requestType,
    	contentType: contentType,
    	// The type of data we expect back
    	dataType : dataType
	});
}

function show_modal(mode,title,isApply,isClose,isLarge){
	$("#modalTitle").html(title);
	if (isApply){$("button#btnApply").show();}
	else{$("button#btnApply").hide();}
	if (isClose){$("button#btnClose").show();}
	else{$("button#btnClose").hide();}
	if (isLarge){
		$(".modal-dialog").addClass("modal-lg");
	}
	$("#modalDialog").modal('show');

	// Loading modal content from server
	CreateAJAX("/modal/"+mode,"GET","html",{})
	.done(function(response){
		$("#modalContent").html(response);
	})
	.fail(function(xhr){
		$("#modalContent").html(xhr.responseText);
	});

}

function hide_modal(){$("#modalDialog").modal('hide');}

function select_all(){
	//console.log($("table").find("input[id!='selectAll']"));
	$("table").find("input[id!='selectAll']")
		.prop("checked",$("input#selectAll").is(":checked"));
}

function show_alert(type,message){
    $("div#panelAlert").removeClass("alert")
    .removeClass("alert-warning")
    .removeClass("alert-danger")
    .removeClass("alert-info")
    .removeClass("alert-success")
    .removeClass("alert-dismissible");
	switch(type)
	{
		case TYPE_INFO: // INFO
			$("div#panelAlert").addClass("alert").addClass("alert-info").addClass("alert-dismissible");
			break;
		case TYPE_ERROR: // ERROR
			$("div#panelAlert").addClass("alert").addClass("alert-danger").addClass("alert-dismissible");
			break;
		case TYPE_WARN: // WARN
			$("div#panelAlert").addClass("alert").addClass("alert-warning").addClass("alert-dismissible");
			break;
		case TYPE_SUCCESS:
			$("div#panelAlert").addClass("alert").addClass("alert-success").addClass("alert-dismissible");
			break;
	}
	$("span#alertMessage").html(message);
	$("div#panelAlert").show();
}
function hide_alert(type,message){
	$("div#panelAlert").hide();
}
$(document).on("click",".close",function(e){$("#panelAlert").hide();});
$(document).on("click","input#selectAll",function(e){select_all()});
function handle_error(xhr,top){
	var response = jQuery.parseJSON(xhr.responseText);
	showToast("danger",response.message,top);}

function get_current_url(){
	var url = window.location.href;
	var arr = url.split("/");
	return arr[0] + "//" + arr[2]
}
function scrollTop(){
	$("html, body").animate({ scrollTop: 0 }, "slow");
}
function generate_guid() {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
}

function get_status(sid){
	CreateAJAX("/status/"+sid,"GET","json",{})
	.done(function(response){
		set_progress(response.status+" <img style='margin-left:10px' src='/static/images/495.gif'/>",response.value,total);
	})
	.fail(function(xhr){
		console.log(xhr);
	});
}

function set_progress(status,current,total){
	var percent = (current/total)*100;
	$("#current_status").html(status);
	$("#pBar").css("width",percent.toString()+"%");
	$("#current_progress").html("Processed "+current.toString()+" out of "+total.toString());
}
$(document).on("click","tr#userRow input[type='checkbox']",function(event){
	event.stopPropagation();
});
$(document).on("click","tr#userRow button",function(event){
	event.stopPropagation();
});
$(document).on("click","tr#userRow",function(event){
	var checkbox = $(this).find("input[type='checkbox']");
	checkbox.trigger("click");
});

function formatDate(date) {
  var monthNames = [
    "January", "February", "March",
    "April", "May", "June", "July",
    "August", "September", "October",
    "November", "December"
  ];

  var day = date.getDate();
  var monthIndex = date.getMonth();
  var year = date.getFullYear();

  return day + ' ' + monthNames[monthIndex] + ' ' + year;
}