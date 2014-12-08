// Welcome route controller
// Redirect to logout route when user press logout in welcome screen
App.UserWelcomeController = Ember.Controller.extend({

	needs : 'clusterCreate',

	sortdir : false,
	actions : {
		sortBy : function(param) {
			this.set('sortProperties', [param]);
			this.set('sortdir', !this.get('sortdir'));
			this.set('sortAscending', this.get('sortdir'));
		},
	}
});
