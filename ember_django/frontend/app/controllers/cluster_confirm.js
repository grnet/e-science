// Cluster/confirm controller
App.ClusterConfirmController = Ember.Controller.extend({
	// in order to have access to Cluster/create controller
	needs : 'clusterCreate',
	message : '',
	// return to previous screen (cluster/create)
	go_back : function() {
		// reset some variables
		this.controllerFor('clusterCreate').set('master_enabled', false);
		this.controllerFor('clusterCreate').set('master_color', "lightblue");
		this.controllerFor('clusterCreate').set('slaves_enabled', false);
		this.controllerFor('clusterCreate').set('slaves_color', "lightblue");
		this.controllerFor('clusterCreate').set('storage_Not_Allow', true);
	},
	actions : {
		// logout functionality
		logout : function() {
			// clear variables in  cluster/create
			this.controllerFor('clusterCreate').reset_variables();
			// redirect to logout
			this.transitionTo('user.logout');
		},
		// when previous button is pressed
		// go_to_flavor action is triggered
		go_to_flavor : function() {
			this.set('message', '');
			this.go_back();
			// redirect
			this.transitionTo('cluster.create');
		},
		// when next button is pressed
		// go_to_create action is triggered
		// User's cluster creation choices are send to backend for checking
		go_to_create : function() {
			var self = this;
			// PUT request
			var cluster_selection = this.store.update('clusterchoice', {
			  // set the clusterchoice model with the user choices
				'id' : 1,
				'cluster_name' : this.controllerFor('clusterCreate').get('cluster_name'),
				'cluster_size' : this.controllerFor('clusterCreate').get('cluster_size'),
				'cpu_master' : this.controllerFor('clusterCreate').get('master_cpu_selection'),
				'mem_master' : this.controllerFor('clusterCreate').get('master_mem_selection'),
				'disk_master' : this.controllerFor('clusterCreate').get('master_disk_selection'),
				'cpu_slaves' : this.controllerFor('clusterCreate').get('slaves_cpu_selection'),
				'mem_slaves' : this.controllerFor('clusterCreate').get('slaves_mem_selection'),
				'disk_slaves' : this.controllerFor('clusterCreate').get('slaves_disk_selection'),
				'disk_template' : this.controllerFor('clusterCreate').get('disk_temp'),
				'os_choice' : this.controllerFor('clusterCreate').get('operating_system')
			}).save();
			cluster_selection.then(function(data) {
				// Set the response to user's create cluster click when put succeeds.
				self.set('message', data._data.message);
			}, function() {
				// Set the response to user's create cluster click when put fails.
				self.set('message', 'A problem occured during your request. Please check your cluster parameters and try again');
			});
		}
	}
}); 
