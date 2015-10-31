// features/screenshots route
App.FeaturesVideosRoute = Ember.Route.extend({
    model : function(params, transition){
        var that = this;
        return this.store.fetch('video', {}).then(function(videos) {
            return videos.get('content');
        }, function(reason) {
            console.log(reason.message);
        });
    }
});
