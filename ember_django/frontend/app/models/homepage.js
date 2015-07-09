attr = App.attr;
// Model for Orka Clusters Statistics 
// Active and Spawned clusters
App.Homepage = DS.Model.extend({
    spawned_clusters : attr('number'),
    active_clusters : attr('number')
});
