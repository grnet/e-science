// Welcome user route.
// Show user id, number of clusters and table of clusters.
App.UserWelcomeRoute = App.RestrictedRoute.extend({
	//"user" model for the welcome route
	needs : 'userWelcome',

	model : function(params, transition) {
		$.loader.close(true);
		// Return user record with id 1.
		// If user record not in store, perform a GET request
		// and get user record from server.
		var that = this;
		var promise = this.store.fetch('user', 1);
		promise.then(function(user) {
			// success
			var num_records = user.get('clusters').get('length');
			var bPending = false;
			for ( i = 0; i < num_records; i++) {
				if (user.get('clusters').objectAt(i).get('cluster_status') == '2') {
					that.controllerFor('userWelcome').send('timer', true, that.store);
					bPending = true;
					break;
				}
			}
			if (!bPending) {
				that.controllerFor('userWelcome').send('timer', false);
			}
		}, function(reason) {
			// failure
			console.log(reason.message);
		});
		return promise;
	},
	afterModel : function(user, transition) {
		// if we came from a link-to helper that doesn't fire the model hook
		var that = this;
		var num_records = user.get('clusters').get('length');
		var bPending = false;
		for ( i = 0; i < num_records; i++) {
			if (user.get('clusters').objectAt(i).get('cluster_status') == '2') {
				that.controllerFor('userWelcome').send('timer', true, that.store);
				bPending = true;
				break;
			}
		}
		if (!bPending) {
			that.controllerFor('userWelcome').send('timer', false);
		}
	},
	actions : {
		willTransition : function(transition) {
			// leaving this route
			this.controller.send('timer', false);
		},
		didTransition : function() {
			// arrived at this route
			Ember.run.later(this, function() {
				Ember.run.later(this, function() {
					this.controller.set('sortbyname', true);
					this.controller.set('sortbyname', false);
					console.log('sort send');
				}, 1000);
				this.controller.send('timer', true);
				console.log('action send');
			}, 1500);
			return true;
		}
	},
	deactivate : function() {
		// left this route
		this.controller.send('timer', false);
	},
});

