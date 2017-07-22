var rowItems;
$(document).ready(function(){
	// Listing templates
	list_templates();

	// Attaching handlers
	$("button").click(button_handler);
});

function list_templates(){

	$("#templatesList").html(TPL_LOADING);
	CreateAJAX("/tpls/list","GET","json",{})
	.done(function(response){
		$.get("/static/templates/templates.list.html",function(template){
			tplList = Handlebars.compile(template);
			$("#templatesList").html(tplList(response));
			rowItems = $("table#tblTpls tr");
		});
	})
	.fail(function(xhr){
		$("#templatesList").html(xhr.responseText);
	});
}

function button_handler(event){
	var id = event.currentTarget.id;
	switch(id){
		case "btnCreate":
			show_modal("createtpl","Create new template",true,true);
			break;
		case "btnApply":
			create_template();
			break;
		case "btnDelete":
			if ($("input[id!='selectAll']:checked").length == 0){
				show_alert(TYPE_ERROR,"Select at least one template to delete");
				return;
			}
			if (window.confirm("Are you sure that you want to delete selected template(s)?")){
				delete_templates();} 			
			break;
	}

}


function create_template()
{
	var txtName = $("input#txtName");	
	// Checking
	if (txtName.val() == ""){show_alert(TYPE_ERROR,"Template's name is mandatory");txtName.focus();return;}
	template = Template.init($("#modalContent"));
	template.create();	
}

function delete_templates(){

	tpls = new Array();
	$("input[id!='selectAll']:checked").each(function(){tpls.push(this.id);});
	Template.delete(tpls);
}

$(document).on("click","button#btnAddPolicy",function(){
	if ($("#txtPolicyID").val() != ""){
		$("table#tblPolicies tbody")
		.append("<tr><td><span class=\"glyphicon glyphicon-remove removeIcon\" aria-hidden=\"true\"></span></td><td id='tdPolicy'>"+$("#txtPolicyID")
			.val()+"</td></tr>");
	}
});
$(document).on("click",".removeIcon",function(){$(this).closest('tr').remove();});
$( document ).ajaxComplete(function(event,xhr,settings) {
  	switch (settings.url){
  		case "/tpls/delete":list_templates();break;
  		case "/tpls/create":$("#modalDialog").modal("hide");list_templates();break;
  	}
});
$(document).on("keyup","input#txtSearch",function(){
	var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
	rowItems.show().filter(function() {
		var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
		return !~text.indexOf(val);
	}).hide();
});

