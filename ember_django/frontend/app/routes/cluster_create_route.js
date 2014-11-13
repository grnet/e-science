// Createcluster index route (/cluster/create url)
App.ClusterCreateRoute = App.RestrictedRoute.extend({
    // model for create cluster choices (input form)
    model : function() {
	return this.store.find('cluster', 1);
    }
});
