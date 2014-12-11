// Welcome route controller
// Redirect to logout route when user press logout in welcome screen
App.UserWelcomeController = Ember.Controller.extend({

	needs : 'clusterCreate',
	output_message : '', // output message of create cluster script
	create_cluster_start : false, // flag to see if the transition is from create cluster button

	sortedclusters : [],
	column : '',
	sortdir : false,
	sortedCollection: function() {
		return Ember.ArrayProxy.createWithMixins(Ember.SortableMixin, {
			content: this.get('sortedclusters'),
			sortProperties: [this.get('column')],
			sortAscending: this.get('sortdir')
		});
	}.property('sortdir'),
	actions : {
		sortBy : function(clusters, column) {
			this.set('sortedclusters', clusters);
			this.set('column', column);
			this.set('sortdir', !this.get('sortdir'));
			console.log(String(this.get(sortdir)));
		}
	},
});
