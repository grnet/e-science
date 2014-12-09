attr = App.attr;
// User model used in our app (welcome screen)
App.User = DS.Model.extend({
	token : attr('string'), // okeanos token
	user_id : attr('number'), // user_id in backend database
	clusters : DS.hasMany('userCluster', {
		async : true,
		embedded : true
	}), // user cluster records
	cluster : function() {
		return this.get('clusters.length');
	}.property('clusters.length'),
});

App.UserCluster = DS.Model.extend({
	cluster_name : attr('string'), // name of the cluster
	cluster_size : attr('number'), // size of cluster (master+slaves)
	cluster_status : attr('string'), // status of cluster
	user : DS.belongsTo('user'), // user that created the cluster
});

App.User.reopenClass({
	FIXTURES : [{
		id : 1,
		token : "PLACEHOLDER",
		cluster : 3,
		clusters : [1, 2, 3]
	}]
});

App.UserCluster.reopenClass({
	FIXTURES : [{
		id : 1,
		cluster_name : "acluster",
		cluster_size : 5,
		cluster_status : "PENDING",
		user : 1
	}, {
		id : 2,
		cluster_name : "fcluster",
		cluster_size : 3,
		cluster_status : "ACTIVE",
		user : 1
	}, {
		id : 3,
		cluster_name : "ecluster",
		cluster_size : 12,
		cluster_status : "DESTROYED",
		user : 1
	}]
});
