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
			// console.log('route > model > num_records ' + num_records);
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
			console.log(reason.statusText);
			transition.abort();
		});
		return promise;
	},
	afterModel : function(user, transition) {
		// if we came from a link-to helper that doesn't fire the model hook
		// console.log(user.get('clusters').get('length'));
		this.controllerFor('userWelcome').send('sortBy', user.get('clusters'), 'action_date');
		this.controllerFor('userWelcome').send('sortBy', user.get('clusters'), 'action_date');
		if ((user.get('user_theme') !== "")&&(user.get('user_theme') !== undefined)&&(user.get('user_theme') !== null)) {
			changeCSS(user.get('user_theme'), 0);			
		}
	},
	actions : {
		willTransition : function(transition) {
			// leaving this route
			this.controller.send('timer', false);
		},
		didTransition : function() {
			// arrived at this route
			var from_create = this.controller.get('create_cluster_start');
			var times_refreshed = this.controller.get('refreshed');
			if (from_create && (times_refreshed <= 10)) {
				// this.controller.set('create_cluster_start', false);
				Ember.run.later(this, function() {
					// console.log('route > debouncing refresh'); //debug
					this.controller.set('refreshed', this.controller.get('refreshed') + 1);
					// console.log(this.controller.get('refreshed')); //debug
					this.controller.send('doRefresh');
				}, 3000);
			} else if (!from_create) {
				this.controller.set('refreshed', 0);
			}
			return true;
		},
		deleteCluster : function(cluster) {
			var that = this;
			cluster.set('cluster_confirm_delete', false);
			cluster.destroyRecord().then(function(data){
				var times_refreshed = that.controller.get('refreshed');
				var refresh = Math.max(5, times_refreshed);
				that.controller.set('refreshed', 10-refresh);
				that.controller.set('create_cluster_start', true);
				Ember.run.later(that, function() {
					that.controller.send('doRefresh');
				}, 1000);
			},function(reason){
				console.log(reason.message);
				that.controller.set('output_message', reason.message);
			});
		},
		confirmDelete : function(cluster, value) {
			cluster.set('cluster_confirm_delete', value);
		},
		error: function(err) {
			// to catch errors
			// for example 401 responses
			this.transitionTo('user.logout');
    	}
	},
	deactivate : function() {
		// left this route
		this.controller.send('timer', false);
	}
});

