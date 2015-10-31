// features/screenshots route
App.FeaturesScreenshotsRoute = Ember.Route.extend({
    model : function(params, transition){
        var that = this;
        return this.store.fetch('screen', {}).then(function(screens) {
            return screens.get('content');
        }, function(reason) {
            console.log(reason.message);
        });
    }
});