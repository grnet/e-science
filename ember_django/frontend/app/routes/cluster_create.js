// Cluster Create route
App.ClusterCreateRoute = App.RestrictedRoute.extend({
	needs : 'clusterCreate',
	// model for create cluster choices (input form)
	model : function() {
		$.loader.close(true);
		return this.store.find('cluster');
	},
	afterModel : function() {
		// resets variables every time you go to the create cluster
		this.controllerFor('clusterCreate').reset_variables();
		this.controllerFor('clusterCreate').reset_project();
	},
});
