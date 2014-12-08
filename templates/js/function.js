jQuery.noConflict();

// https://docs.djangoproject.com/en/dev/ref/csrf/
function doCSRF() {
	function getCookie(name){
		var cookieValue = null;
		if (document.cookie && document.cookie != ''){
			var cookies = document.cookie.split(';');
			for (var i = 0; i < cookies.length; i++) {
				var cookie = jQuery.trim(cookies[i]);
				if (cookie.substring(0,name.length+1) == (name+'=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	}

	var csrftoken = getCookie('csrftoken');

	// Change token

	jQuery(document).ready(function($){
		if(csrftoken != null){
			$("input.CSRFToken").attr('value',csrftoken);
		} else {
			location.href = "lostcsrf/doToken/";
		}
	});
}
