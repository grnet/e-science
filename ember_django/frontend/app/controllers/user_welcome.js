// User Welcome controller
App.UserWelcomeController = Ember.Controller.extend({

	needs : 'clusterCreate',
	// output message of create cluster script
	output_message : '',
	// flag to see if the transition is from create cluster button
	create_cluster_start : false,

	sortedclusters : [],
	column : '',
	sortdir : null,
	sortbyname : false,
	sortbystatus : false,
	sortbysize : false,
	sortbyurl : false,
	confirm : false,
	ip_of_master : '',
	sortedCollection : function() {
		// sorts content (clusters) based on properties
		return Ember.ArrayProxy.createWithMixins(Ember.SortableMixin, {
			content : this.get('sortedclusters'),
			sortProperties : [this.get('column')],
			sortAscending : this.get('sortdir')
		});
	}.property('sortdir', 'sortbyname', 'sortbystatus', 'sortbysize', 'sortbyurl'),
	actions : {
		// sorts clusters based on selected column (name, status, size, IP)
		sortBy : function(clusters, column) {
			switch (column) {
			case 'cluster_name':
				this.set('sortbyname', !this.get('sortbyname'));
				this.set('sortdir', this.get('sortbyname'));
				break;
			case 'cluster_status':
				this.set('sortbystatus', !this.get('sortbystatus'));
				this.set('sortdir', this.get('sortbystatus'));
				break;
			case 'cluster_size':
				this.set('sortbysize', !this.get('sortbysize'));
				this.set('sortdir', this.get('sortbysize'));
				break;
			case 'master_IP':
				this.set('sortbyurl', !this.get('sortbyurl'));
				this.set('sortdir', this.get('sortbyurl'));
				break;
			}
			this.set('sortedclusters', clusters);
			this.set('column', column);
		},
		go_to_confirm : function(master_IP) {
			this.set('confirm', true);
			this.set('ip_of_master', master_IP);
			alert(master_IP);
		},
		go_to_destroy : function(master_IP) {

		},
		timer : function(status, store) {
			var that = this;
			if (Ember.isNone(this.get('timer'))) {
				this.set('timer', App.Ticker.create({
					seconds : 5,
					onTick : function() {
						if (!store) {
							store = that.store;
						}
						if (store && that.controllerFor('application').get('loggedIn')) {
							var promise = store.fetch('user', 1);
							promise.then(function(user) {
								// success
								var num_records = user.get('clusters').get('length');
								var bPending = false;
								for ( i = 0; i < num_records; i++) {
									if (user.get('clusters').objectAt(i).get('cluster_status') == '2') {
										bPending = true;
										break;
									}
								}
								if (!bPending) {
									that.get('timer').stop();
									status = false;
								}
							}, function(reason) {
								that.get('timer').stop();
								status = false;
								console.log(reason);
							});
							return promise;
						}
					}
				}));
			} else {
				if (status) {
					that.get('timer').start();
				} else {
					that.get('timer').stop();
				}
			}
			if (status) {
				this.get('timer').start();
			} else {
				this.get('timer').stop();
			}
		},
	},
});
