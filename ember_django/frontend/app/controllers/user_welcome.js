// User Welcome controller
App.UserWelcomeController = Ember.Controller.extend({

	needs : 'clusterCreate',
	// output message of create cluster script
	output_message : '',
	// flag to see if the transition is from create cluster button
	create_cluster_start : false,

	tick : false, // temp for debug

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
			console.log('timer called with: ' + String(status));
			if (Ember.isNone(this.get('timer'))) {
				this.set('timer', App.Ticker.create({
					seconds : 3,
					onTick : function() {
						this.set('tick', !this.get('tick'));
						console.log(this.get('tick'));
						return store.fetch('user', 1);
					}
				}));
			}
			if (status) {
				this.get('timer').start();
			} else {
				this.get('timer').stop();
			}
		},
	},
});
