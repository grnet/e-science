// Createcluster resource functionality
// Createcluster index route (/cluster/create url)
App.CreateclusterIndexRoute = App.RestrictedRoute.extend({
    model : function() {
	return this.store.find('createcluster', 1);
    }
});
