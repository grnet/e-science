App.ClusterManagmentRoute = App.RestrictedRoute.extend({
	needs : 'clusterManagment',
	// model for create cluster choices (input form)
	model : function() {
		$.loader.close(true);
		return this.store.find('cluster');
	}
	
});