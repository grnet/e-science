attr = App.attr;
// User model used in our app (welcome screen)
App.User = DS.Model.extend({
	token : attr('string'), 				// okeanos token
	user_id : attr('number'), 				// user_id in backend database
	clusters : DS.hasMany('userCluster', {
		async : true,
	}), 									// user cluster records
	cluster : attr(),
	// cluster : function() {
	// return this.get('clusters.length');
	// }.property('clusters.length'),
});

App.UserCluster = DS.Model.extend({
	cluster_name : attr('string'), 				// name of the cluster
	cluster_size : attr('number'), 				// size of cluster (master+slaves)
	cluster_status : attr('string'), 			// status of cluster
	master_IP : attr('string'), 				// master ip
	cpu_master : attr(),
	mem_master : attr(),
	disk_master : attr(),
	cpu_slaves : attr(),
	mem_slaves : attr(),
	disk_slaves : attr(),
	disk_template : attr(),
	os_image : attr(),
	project_name : attr(),
	user : DS.belongsTo('user'), // user that created the cluster
	cluster_url : function() {
		return 'http://' + this.get('master_IP') + ':8088/cluster';
	}.property('master_IP'),
	cluster_status_verbose : function() {
		var status = this.get('cluster_status');
		switch (status) {
		case "0":
			return "DESTROYED";
		case "1":
			return "ACTIVE";
		case "2":
			return "PENDING";
		default:
			return "UNKNOWN";
		}
	}.property('cluster_status'),
	cluster_status_class : function()
	{
		var status = this.get('cluster_status');
		switch (status) {
		case "0":
			return "glyphicon glyphicon-remove text-danger";
		case "1":
			return "glyphicon glyphicon-ok text-success";
		case "2":
			return "glyphicon glyphicon-time text-warning";
		default:
			return "glyphicon glyphicon glyphicon-question-sign text-muted";
		}
	}.property('cluster_status'),
});

// App.User.reopenClass({
// FIXTURES : [{
// id : 1,
// token : "PLACEHOLDER",
// cluster : 3,
// clusters : [1, 2, 3]
// }]
// });
//
// App.UserCluster.reopenClass({
// FIXTURES : [{
// id : 1,
// cluster_name : "acluster",
// cluster_size : 5,
// cluster_status : "PENDING",
// user : 1
// }, {
// id : 2,
// cluster_name : "fcluster",
// cluster_size : 3,
// cluster_status : "ACTIVE",
// user : 1
// }, {
// id : 3,
// cluster_name : "ecluster",
// cluster_size : 12,
// cluster_status : "DESTROYED",
// user : 1
// }]
// });
