attr = App.attr;
// Information about user (welcome screen)
App.Homepage = DS.Model.extend({
    spawned_clusters : attr('number'),
    active_clusters : attr('number')

});