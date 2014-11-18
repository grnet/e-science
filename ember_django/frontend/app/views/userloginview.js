// Login view
// After user submits ~okeanos token, sends it to login controller
App.UserLoginView = Ember.View.extend({
    submit : function() {
	// retrieve token
	var text = this.get('controller.token');
	// send it to the login action
	this.get('controller').send('login', text);
    }
});
