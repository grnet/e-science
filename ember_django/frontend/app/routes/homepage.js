App.HomepageRoute = Ember.Route.extend({
    controllerName: 'homepage',
    // model for cluster management route
    model : function(params) {
        var that = this;
        // find the correct cluster
        this.store.find('homepage', 1).then(function(homepage) {
            
            that.controller.set('spawned_clusters', homepage.get('spawned_clusters'));
            that.controller.set('active_clusters', homepage.get('active_clusters'));
            return homepage;
        }, function(reason) {
            console.log(reason.message);
        });
    }
}); 