// Cluster/create route (/cluster/create url)
App.ClusterCreateRoute = App.RestrictedRoute.extend({
    needs: 'clusterCreate',
    // model for create cluster choices (input form)
    model : function() {
	return this.store.find('cluster', 1);
    },
    afterModel : function() {
	// resets variables every time you go to the create cluster
	this.controllerFor('clusterCreate').reset_variables();
    },
});
