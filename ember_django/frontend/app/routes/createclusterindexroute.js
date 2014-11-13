// Createcluster index route (/cluster/create url)
App.CreateclusterIndexRoute = App.RestrictedRoute.extend({
    // model for create cluster choices (input form)
    model : function() {
	return this.store.find('createcluster', 1);
    }
});
