// Welcome route controller
// Redirect to logout route when user press logout in welcome screen
App.UserWelcomeController = Ember.Controller.extend({

	needs : 'clusterCreate',
	output_message : '', // output message of create cluster script
	create_cluster_start : false, // flag to see if the transition is from create cluster button
	sortdir : false,
	actions : {
		sortBy : function(clusters, column) {
			// console.log(clusters);
			// console.log(column);
			clusters.set('sortProperties', [column]);
			this.set('sortdir', !this.get('sortdir'));
			clusters.set('sortAscending', this.get('sortdir'));
		},
	},
});
