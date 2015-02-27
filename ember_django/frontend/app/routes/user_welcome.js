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
				if ((user_clusters.objectAt(i).get('cluster_status') == '2')
					||(user_clusters.objectAt(i).get('hadoop_status') == '2')) {
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
		var lastsort = this.controllerFor('userWelcome').get('column');
		if (!Ember.isBlank(lastsort)) {
			this.controllerFor('userWelcome').send('sortBy', user_clusters, lastsort);
			this.controllerFor('userWelcome').send('sortBy', user_clusters, lastsort);
		} else {
			this.controllerFor('userWelcome').send('sortBy', user_clusters, 'action_date');
			this.controllerFor('userWelcome').send('sortBy', user_clusters, 'action_date');
		}
		if ((user.get('user_theme') !== "") && (user.get('user_theme') !== undefined) && (user.get('user_theme') !== null)) {
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
			if (from_create) {
				this.controller.set('count', 10);
				this.controller.send('timer', true, this.store);
			}
            else {
                this.controller.set('output_message', '');
            }
			return true;
		},
		takeAction : function(cluster) {
			var self = this;
			var store = this.store;
			var action = cluster.get('cluster_confirm_action');
			cluster.set('cluster_confirm_action', false);
			switch(action) {
			case 'cluster_delete':
				cluster.destroyRecord().then(function(data) {
					var count = self.controller.get('count');
					var extend = Math.max(5, count);
					self.controller.set('count', extend);
					self.controller.set('create_cluster_start', true);
					self.controller.send('timer', true, store);
				}, function(reason) {
					console.log(reason.message);
					self.controller.set('output_message', reason.message);
				});
				break;
			case 'hadoop_start':
				cluster.set('hadoop_status','start');
				cluster.save().then(function(data){
					var count = self.controller.get('count');
					var extend = Math.max(5, count);
					self.controller.set('count', extend);
					self.controller.set('create_cluster_start', true);
					self.controller.send('timer', true, store);
				},function(reason){
					console.log(reason.message);
					self.controller.set('output_message', reason.message);
				});
				break;
			case 'hadoop_stop':
				cluster.set('hadoop_status','stop');
				cluster.save().then(function(data){
					var count = self.controller.get('count');
					var extend = Math.max(5, count);
					self.controller.set('count', extend);
					self.controller.set('create_cluster_start', true);
					self.controller.send('timer', true, store);
				},function(reason){
					console.log(reason.message);
					self.controller.set('output_message', reason.message);
				});
				break;
			case 'hadoop_format':
				cluster.set('hadoop_status','format');
				cluster.save().then(function(data){
					var count = self.controller.get('count');
					var extend = Math.max(5, count);
					self.controller.set('count', extend);
					self.controller.set('create_cluster_start', true);
					self.controller.send('timer', true, store);
				},function(reason){
					console.log(reason.message);
					self.controller.set('output_message', reason.message);
				});
				break;
			}
		},
		confirmAction : function(cluster, value) {
			cluster.set('cluster_confirm_action', value);
		},
		error : function(err) {
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

