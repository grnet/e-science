// Main application controller
// loggedIn, homeURL, adminURL, STATIC_URL
App.ApplicationController = Ember.Controller.extend({
	needs : 'userWelcome',
	loggedIn : false,
	homeURL : function() {
		if (this.get('loggedIn')){
			return "#/user/welcome";
		}else {
			return "#/";
		}
	}.property('loggedIn'),
	adminURL : function() {
		var admin_url = window.location.origin + "/admin";
		return admin_url;
	}.property(),
	STATIC_URL : DJANGO_STATIC_URL,

	userTheme : user_themes,

	actions : {
		change_theme : function(cssUrl) {
			var self = this;
			changeCSS(cssUrl, 0);
			// PUT user_theme to Django backend, when selected.
			if (cssUrl) {
				this.store.find('user', 1).then(function(user) {
					user.set('user_theme', cssUrl);
					self.store.push('user', self.store.normalize('user', {
						'id' : 1,
						'user_theme' : user.get('user_theme')
					})).save();
				});
			}
		}
	}
});