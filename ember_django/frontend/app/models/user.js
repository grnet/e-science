attr = App.attr;
// User model used in our app (welcome screen)
App.User = DS.Model.extend({
	token : attr('string'), 				// okeanos token
	user_id : attr('number'), 				// user_id in backend database
	clusters : DS.hasMany('userCluster'), 	// user cluster records
	cluster : function() {
		return this.get('clusters.length');
	}.property('clusters.length'),
});

App.UserCluster = DS.Model.extend({
	cluster_name : attr('string'), 			// name of the cluster
	cluster_size : attr('number'), 			// size of cluster (master+slaves)
	user : DS.belongsTo('user')				// user that created the cluster
});
