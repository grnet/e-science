App.ClusterManagementRoute = App.RestrictedRoute.extend({
	
  model: function(params) {
	  	console.log("---> ");
		console.log(params);
		console.log(params["usercluster.cluster_name"]);

		var self = this;
		var sel_cluster;
		this.store.fetch('user', 1).then(function(user) {
		var clusters = user.get('clusters');

		var length = clusters.get('length');
		if (length > 0) {

			for (var i = 0; i < length; i++) {
				if (clusters.objectAt(i).get('cluster_name') == params["usercluster.cluster_name"])
				{
					self.set('sel_cluster', clusters.objectAt(i));
				}
			}
		}
	
 	}, function(reason) {
		console.log(reason.message);
	});
 	return this.get('sel_cluster');
  }
  
});