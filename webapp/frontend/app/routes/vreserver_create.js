// VRE server Create route
App.VreserverCreateRoute = App.RestrictedRoute.extend({
	// model for create VRE server choices (input form)
	model : function() {
		$.loader.close(true);
		return this.store.find('vreserver');
	},
	actions: {
		error: function(err) {
			// to catch errors
			// for example 401 responses
			console.log(err['message']);
			this.transitionTo('user.logout');
    	},
    	didTransition: function(transition) {

    	}
	}
});
