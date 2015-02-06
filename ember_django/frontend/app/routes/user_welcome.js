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
			console.log(reason.message);
		});
		return promise;
	},
	afterModel : function(user, transition) {
		// if we came from a link-to helper that doesn't fire the model hook
		// console.log(user.get('clusters').get('length'));
		this.controllerFor('userWelcome').send('sortBy', user.get('clusters'), 'cluster_name');
		this.controllerFor('userWelcome').send('sortBy', user.get('clusters'), 'cluster_name');
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
				this.set('refreshed', 0);
			}
			return true;
		},
		deleteCluster : function(cluster) {
			var that = this;
			// this.store.find('user', 1).then(function(data){
				// data.store.find('user-cluster', cluster.get('id')).then(function(data){
					// data.destroyRecord();
				// },function(reason){
// 					
				// });
			// },function(reason){
// 				
			// });		
			cluster.deleteRecord();
			// cluster.destroyRecord();
		}
	},
	deactivate : function() {
		// left this route
		this.controller.send('timer', false);
	},
});

