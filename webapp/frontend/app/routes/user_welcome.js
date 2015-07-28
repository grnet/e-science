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
			var user_clusters = user.get('clusters');
			var user_vreservers = user.get('vreservers');
			var num_cluster_records = user_clusters.get('length');
			var num_vre_records = user_vreservers.get('length');
			// console.log('route > model > num_records ' + num_records);
			var bPending = false;
			for ( i = 0; i < num_cluster_records; i++) {
				if ((user_clusters.objectAt(i).get('cluster_status') == '2')
					||(user_clusters.objectAt(i).get('hadoop_status') == '2')) {
					that.controllerFor('userWelcome').send('timer', true, that.store);
					bPending = true;
					break;
				}
			}
			for ( i = 0; i < num_vre_records; i++) {
                if (user_vreservers.objectAt(i).get('server_status') == '2') {
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
		if ((user.get('user_theme') !== "") && (user.get('user_theme') !== undefined) && (user.get('user_theme') !== null)) {
			changeCSS(user.get('user_theme'), 0);
		}
	},
	actions : {
		willTransition : function(transition) {
			// leaving this route
			this.controller.send('timer', false);
			this.controller.send('removeMessage',1,true);
		},
		didTransition : function() {
			// arrived at this route
			var from_create = this.controller.get('create_cluster_start');
			if (from_create) {
				this.controller.set('count', 10);
				this.controller.send('timer', true, this.store);
			}
			return true;
		},
		takeVreAction : function(vreserver){
		    var self = this;
            var store = this.store;
            var action = vreserver.get('action_server_confirm');
            vreserver.set('action_server_confirm', false);
            switch(action) {
            case 'server_delete':
                vreserver.destroyRecord().then(function(data) {
                    var count = self.controller.get('count');
                    var extend = Math.max(5, count);
                    self.controller.set('count', extend);
                    self.controller.set('create_cluster_start', true);
                    self.controller.send('timer', true, store);
                }, function(reason) {
                    console.log(reason.message);
                    if (!Ember.isBlank(reason.message)){
                        var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.controller.send('addMessage',msg);
                    }
                });
                break;
            }
		},
		takeClusterAction : function(cluster) {
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
					if (!Ember.isBlank(reason.message)){
						var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.controller.send('addMessage',msg);
					}
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
					if (!Ember.isBlank(reason.message)){
						var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.controller.send('addMessage',msg);
					}
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
					if (!Ember.isBlank(reason.message)){
						var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.controller.send('addMessage',msg);
					}
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
					if (!Ember.isBlank(reason.message)){
						var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.controller.send('addMessage',msg);
					}
				});
				break;
			}
		},
		confirmVreAction : function(vreserver, value) {
            vreserver.set('action_server_confirm', value);
        },
		confirmClusterAction : function(cluster, value) {
			cluster.set('cluster_confirm_action', value);
			// remove following line comment for easy message panel debug
			// this.controller.send('addMessage',{'msg_type':'info','msg_text':'Lorem ipsum dolor sit amet.'+ String(Math.floor(Math.random() * 11))});
		},
		error : function(err) {
			// to catch errors
			// for example 401 responses
			console.log(err['message']);
			this.transitionTo('user.logout');
		}
	},
	deactivate : function() {
		// left this route
		this.controller.send('timer', false);
	}
});

