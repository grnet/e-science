// Redirect to login screen when user press start in homepage
App.HomepageController = Ember.Controller.extend({
	actions: {
		start : function() {
			this.transitionToRoute('user.login');
		}
	}     
});