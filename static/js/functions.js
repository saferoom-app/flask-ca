function showToast(type,message){
	toastr.options = {
		"closeButton": false,
		"debug": false,"newestOnTop": false,"progressBar": false,
		"positionClass": "toast-bottom-center","preventDuplicates": false,
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