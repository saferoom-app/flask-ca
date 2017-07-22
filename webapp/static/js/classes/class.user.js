/*
	Class defines the User and its oerations:

	create() = function is used to create the user
	
	update() = function used to update the existing user
	
	init(doc)   = function used to initialize the User from Web page elements. 
		>> doc = jQuery document object
	
	delete(id) = static function used to delete User 
		>> id = User ID
*/

class User{
	constructor(){
		this.id = "",
		this.name = "",
		this.email = "",
		this.subject = ""		
	}

	static init(doc){
		var user = new User();
		user.id = parseInt(doc.find("input#txtID").val());
		user.name = doc.find("input#txt_CN").val();
		user.email = doc.find("input#txt_E").val();
		// Generating Subject DN
		var subject = new Array();
		$(".dialog_content").find("input[id^='txt_'],select[id^='txt_']").each(function(){
        	if ($(this).val() != ""){
        		subject.push(this.id.split("_")[1]+"="+$(this).val());
        	}
		});
		user.subject = subject.join(",");
		return user	
	}

	create(){
		// Sending request to server
		CreateAJAX("/users/create","POST","json",JSON.stringify(this))
		.done(function(response){showToast("success",response.message,true);})
		.fail(function(xhr){handle_error(xhr,true);});
	}

	update(){
		// Sending request to server
		CreateAJAX("/users/update","POST","json",JSON.stringify(this))
		.done(function(response){showToast("success",response.message,true);})
		.fail(function(xhr){handle_error(xhr,true);});	
	}

	static delete(ids){
		CreateAJAX("/users/delete","DELETE","json",JSON.stringify(ids))
		.done(function(response){showToast("success",response.message,true);})
		.fail(function(xhr){handle_error(xhr);});
	}
}