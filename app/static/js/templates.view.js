$(document).ready(function(){
	// Getting template
	view_template($("#tpl_id").val());	
});

function view_template(id){
	$("#template_content").html("<img src=\"/static/images/89.gif\"/>");
	CreateAJAX("/tpls/get/"+id,"GET","json",{})
	.done(function(response){
		$.get("/static/templates/template.update.html",function(template){
			tpl = Handlebars.compile(template);
			$("#template_content").html(tpl(response));

			// Setting selected values
			values = new Array();
			$.each(response.template.extensions.ku,function(k,v){values.push(v);});
			$("select#ku").selectpicker("val",values);
			$("select#ku").selectpicker("refresh");
			values = []
			$.each(response.template.extensions.sku,function(k,v){values.push(v);});
			$("select#sku").selectpicker("val",values);
			$("select#sku").selectpicker("refresh");
		});

	})
	.fail(function(xhr){$("#template_content").html(xhr.responseText);});

}
$(document).on("click","button#btnAddPolicy",function(){
	if ($("#txtPolicyID").val() != ""){
		$("table#tblPolicies tbody")
		.append("<tr><td><span class=\"glyphicon glyphicon-remove removeIcon\" aria-hidden=\"true\"></span></td><td id='tdPolicy'>"+$("#txtPolicyID")
			.val()+"</td></tr>");}
});
$(document).on("click",".removeIcon",function(){$(this).closest('tr').remove();});
$(document).on("click","button",buttonHandler);
function buttonHandler(event){
	var id = event.currentTarget.id;
	switch (id){
		case "btnUpdate":
			update_template("update");
			break;
		case "btnSave":
			update_template("create");
			break;
		case "btnDelete":
			if (window.confirm("Are you sure that you want to delete selected template(s)?")){
				Template.delete([$("#tpl_id").val()])
			}
			break;
		case "btnCancel":
            history.go(-1);
			break;
		default:
			return false;
	}
}

function update_template(mode){
	template = Template.init($(document));
	template.id = $("#tpl_id").val();
	template[mode]();	
}
$( document ).ajaxComplete(function(event,xhr,settings) {
  	switch (settings.url){
  		case "/tpls/delete":history.go(-1);break;
  	}
});