// Welcome user route.
// Show user id, number of clusters and table of clusters.
App.UserWelcomeRoute = App.RestrictedRoute.extend({
	//"user" model for the welcome route
	needs : 'userWelcome',
	userclusters : [],
	model : function(params, transition) {
		$.loader.close(true);
		// Return user record with id 1.
		// If user record not in store, perform a GET request
		// and get user record from server.
		var that = this;
		var promise = this.store.fetch('user', 1);
		promise.then(function(user) {
			// success
			var user_clusters = user.get('clusters');
			var num_records = user_clusters.get('length');
			that.set('userclusters', user_clusters);
			// console.log('route > model > num_records ' + num_records);
			var bPending = false;
			for ( i = 0; i < num_records; i++) {
				if (user_clusters.objectAt(i).get('cluster_status') == '2') {
					that.controllerFor('userWelcome').send('timer', true, that.store);
					bPending = true;
					break;
				}
			}
			if (!bPending) {
				if (that.controllerFor('userWelcome').get('count') > 0) {
					that.controllerFor('userWelcome').set('count', that.get('count') - 1);
				} else {
					that.controllerFor('userWelcome').send('timer', false);
				}
			}
		}, function(reason) {
			// failure
			console.log(reason.statusText);
			// transition.abort();
		});
		return promise;
	},
	afterModel : function(user, transition) {
		// if we came from a link-to helper that doesn't fire the model hook
		// console.log(user.get('clusters').get('length'));
		var user_clusters = user.get('clusters');
		this.controllerFor('userWelcome').send('sortBy', user_clusters, 'action_date');
		this.controllerFor('userWelcome').send('sortBy', user_clusters, 'action_date');
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
			if (from_create){
				this.controller.set('count', 10);
				this.controller.send('timer', true, this.store);
			}
			return true;
		},
		deleteCluster : function(cluster) {
			var that = this;
			cluster.set('cluster_confirm_delete', false);
			cluster.destroyRecord().then(function(data){
				var count = that.controller.get('count');
				var extend = Math.max(5, count);
				that.controller.set('count', extend);
				that.controller.send('timer', true, that.store);
				that.controller.set('create_cluster_start', true);
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
			console.log(err.TypeError);
			this.transitionTo('user.logout');
    	}
	},
	deactivate : function() {
		// left this route
		this.controller.send('timer', false);
	}
});

