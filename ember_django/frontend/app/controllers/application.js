App.ApplicationController = Ember.Controller.extend({
	homeURL : function() {
		if (this.get('loggedIn')){
			return "#/user/welcome";
		}else {
			return "#/";
		}
	}.property('loggedIn')
	
});