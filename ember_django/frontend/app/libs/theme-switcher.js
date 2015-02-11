/*
 * Functions for changing CSS style and 
 * keeping cookies of user's choice 
 * 
 */


//var user_themes = new Object();
//user_themes.dark = 'styles/bootstrap.orca.css';
// user_themes.light = 'styles/bootstrap.united.orca.css';
var style_cookie_name = "style";
var style_cookie_duration = 30;

function userThemeFunc(name, url) {
	this.name = name;
	this.url = url;
}

var lightTheme = new userThemeFunc('Light Theme', 'styles/bootstrap.united.orka.css');
var blackTheme = new userThemeFunc('Dark Theme', 'styles/bootstrap.orka.css');
var user_themes = [blackTheme, lightTheme];

function changeCSS(cssFile_URL, cssLinkIndex) {
	var cssFile = DJANGO_STATIC_URL + cssFile_URL;
	var oldlink = document.getElementsByTagName("link").item(cssLinkIndex);
	var newlink = document.createElement("link");
	newlink.setAttribute("rel", "stylesheet");
	newlink.setAttribute("type", "text/css");
	newlink.setAttribute("href", cssFile);

	document.getElementsByTagName("head").item(0).replaceChild(newlink, oldlink);
	$(document).ready(function() {
		$("#myCurrentPage").attr("href", window.location.href);
	});

	set_cookie(style_cookie_name, cssFile_URL, style_cookie_duration);
}

function set_style_from_cookie() {
	var setcssFile = get_cookie(style_cookie_name);
	if ((setcssFile !== "")&&(setcssFile !== undefined)&&(setcssFile !== null)) {
		changeCSS(setcssFile, 0);
	}
}

function set_cookie(cookie_name, cookie_value, lifespan_in_days) {
	var day = new Date();
	day.setTime(day.getTime() + (lifespan_in_days * 24 * 60 * 60 * 1000));
	var expires = "expires=" + day.toGMTString();
	document.cookie = cookie_name + "=" + cookie_value + "; " + expires + "; path=/";
}

function get_cookie(cookie_name) {
	var name = cookie_name + "=";
	var ca = document.cookie.split(';');
	for (var i = 0; i < ca.length; i++) {
		var c = ca[i];
		while (c.charAt(0) == ' ')
		c = c.substring(1);
		if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		}
	}
	return "";
}
