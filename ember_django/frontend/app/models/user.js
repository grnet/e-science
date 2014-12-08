attr = App.attr;
// User model used in our app (welcome screen)
App.User = DS.Model.extend({
	token : attr('string'),      					// okeanos token
	user_id : attr('number'),    					// user_id in backend database
	cluster : attr('number'),     					// number of user clusters
	clusters : DS.hasMany('App.UserCluster'), 		// user cluster records
	// cluster : function() {
        // return this.get('clusters.length');}
});

App.UserCluster = DS.Model.extend({
	cluster_name : attr('string'),		// name of the cluster
	cluster_size : attr('number'),		// size of cluster (master+slaves)
	user : DS.belongsTo('App.User')		// user that created the cluster
});
