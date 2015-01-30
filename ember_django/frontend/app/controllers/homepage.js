// Redirect to login screen when user press start in homepage
App.HomepageController = Ember.Controller.extend({
	actions: {
		start : function() {
			this.transitionToRoute('user.login');
		}
	},
	STATIC_URL : DJANGO_STATIC_URL,
});
