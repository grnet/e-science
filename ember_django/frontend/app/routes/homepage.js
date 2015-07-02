App.HomepageRoute = Ember.Route.extend({

    // model for cluster management route
    model : function(params) {

        // find the correct cluster
        var cluster_statistics = this.store.fetch('home', 1).then(function(home) {
        return home;

        }, function(reason) {
            console.log(reason.message);
        });

    }
}); 