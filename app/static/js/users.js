$(document).ready(function(){
	list_users();
});

$(document).on("click","button",buttonHandler);
function buttonHandler(event){
	var id = event.currentTarget.id;
	switch (id){
		case "btnAdd":
			show_modal("adduser","Create new user",true,true,false);
			break;
		case "btnApply":
			update_user($("#txtOP").val());
			break;
		case "btnDelete":
			if (window.confirm("Are you sure that you want to delete selected user(s)?")){
				delete_users();} 			
			break;
	}
}

function list_users(){
	CreateAJAX("/users/list","POST","json",{})
	.done(function(response){
		$.get("/static/templates/users.list.html",function(template){
            userList = Handlebars.compile(template);
            $("#usersList").html(userList(response));
        });
	})
	.fail(function(){handle_error(xhr,true);});
}

function update_user(mode){
	var user = User.init($(document));
	user[mode]();	
}
$( document ).ajaxComplete(function(event,xhr,settings) {
  	switch (settings.url){
  		case "/users/create":hide_modal();list_users();break;
  		case "/users/update":hide_modal();list_users();break;
  		case "/users/delete":list_users();break;
  	}
});

$(document).on("click","a.userLink",function(event){
	show_modal("getuser/"+this.id,"Update user info",true,true,false);
	event.stopPropagation();
});

function delete_users(){
	users = new Array();
	$("input[id!='selectAll']:checked").each(function(){users.push(this.id);});
	User.delete(users);
}