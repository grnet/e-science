// Cluster/confirm route (/cluster/confirm url)
App.ClusterConfirmRoute = App.RestrictedRoute.extend({
    model : function() {
	// Return user record with id 1.
	// If user record not in store, perform a GET request
	// and get user record from server.
	return this.store.find('user', 1);
    }
});
