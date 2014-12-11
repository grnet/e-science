// Welcome route controller
// Redirect to logout route when user press logout in welcome screen
App.UserWelcomeController = Ember.Controller.extend({

	needs : 'clusterCreate',

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
