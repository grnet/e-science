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
			this.controller.send('setActiveTab','clusters');
		},
		didTransition : function() {
			// arrived at this route
			var from_create = this.controller.get('create_cluster_start');
			if (from_create) {
				this.controller.set('count', 15);
				this.controller.send('timer', true, this.store);
			}
			return true;
		},
		takeDslAction : function(dsl){
            var self = this;
            var store = this.store;
            var action = dsl.get('action_dsl_confirm');
            dsl.set('action_dsl_confirm', false);
            switch(action) {
            case 'dsl_delete':
                dsl.destroyRecord().then(function(data) {
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
            case 'dsl_replay':

                // retrieve parameters from yaml            
                

                // create cluster
                // unload cached records
                this.store.unloadAll('clusterchoice');
                var cluster_selection = this.store.push('clusterchoice', {
                    // set the clusterchoice model with the user choices
                    'id' : 1,
                    'project_name' : self.get('project_name'),
                    'cluster_name' : self.get('cluster_name'),
                    'cluster_size' : self.get('cluster_size'),
                    'cpu_master' : self.get('master_cpu_selection'),
                    'ram_master' : self.get('master_ram_selection'),
                    'disk_master' : self.get('master_disk_selection'),
                    'cpu_slaves' : self.get('slaves_cpu_selection'),
                    'ram_slaves' : self.get('slaves_ram_selection'),
                    'disk_slaves' : self.get('slaves_disk_selection'),
                    'disk_template' : self.get('disk_temp'),
                    'os_choice' : self.get('operating_system'),
                    'ssh_key_selection' : self.get('ssh_key_selection'),
                    'replication_factor' : self.get('replication_factor'),
                    'dfs_blocksize': self.get('dfs_blocksize'),
                    'admin_password': self.get('admin_password')
                }).save();
                    
                this.message_hue_login();
                    
                cluster_selection.then(function(clusterchoice) {
                    // Set the response to user's create cluster click when put succeeds.
                    $.loader.close(true);
                    var message = clusterchoice.get('data').message || "";
                    self.set('message', message);
                    if (!Ember.isBlank(message)){
                        var msg = {'msg_type':'danger','msg_text':message};
                        self.get('controllers.userWelcome').send('addMessage',msg);
                    }
                    self.set('controllers.userWelcome.create_cluster_start', true);
                    self.store.fetch('user', 1).then(function(user){
                        self.get('controllers.userWelcome').send('setActiveTab','clusters');
                        self.transitionToRoute('user.welcome');
                    },function(reason){
                        console.log(reason.message);
                    });
                }, function(reason) {
                    // Set the response to user's create cluster click when put fails.
                    console.log(reason.message);
                    $.loader.close(true);
                    self.set('message', reason.message);
                    if (!Ember.isBlank(reason.message)){
                        var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.get('controllers.userWelcome').send('addMessage',msg);
                    }
                    self.set('controllers.userWelcome.create_cluster_start', false);
                    self.store.fetch('user', 1);
                });
                break;
            }
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
		confirmDslAction : function(dsl, value) {
            dsl.set('action_dsl_confirm', value);
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

