App.ClusterManagementRoute = App.RestrictedRoute.extend({
	
	model: function(params) {

		var self = this;

		var selected_cluster = this.store.fetch('user', 1).then(function(user) {

			var clusters = user.get('clusters');

			var length = clusters.get('length');
			if (length > 0) {

				for (var i = 0; i < length; i++) {
					if (clusters.objectAt(i).get('id') == params["usercluster.id"])
					{
						self.set('sel_cluster', clusters.objectAt(i));
						//alert(clusters.objectAt(i).get('cluster_name'));
					 	return clusters.objectAt(i);
					}
				}
			}
	
 			}, function(reason) {
				console.log(reason.message);
			});

	 	return selected_cluster;
	},
	
	actions: {
		
		takeAction : function(cluster) {
			var self = this;
			var store = this.store;
			var action = cluster.get('cluster_confirm_action');
			cluster.set('cluster_confirm_action', false);
			switch(action) {
			case 'cluster_delete':
				cluster.destroyRecord().then(function(data) {
					var count = self.controller.get('count');
					var extend = Math.max(5, count);
					self.controller.set('count', extend);
					self.controller.set('create_cluster_start', true);
					self.controller.send('timer', true, store);
				}, function(reason) {
					console.log(reason.message);
					if (!Ember.isBlank(reason.message)){
						var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.controller.send('addMessage',msg);
					}
				});
				break;
			case 'hadoop_start':
				cluster.set('hadoop_status','start');
				cluster.save().then(function(data){
					var count = self.controller.get('count');
					var extend = Math.max(5, count);
					self.controller.set('count', extend);
					self.controller.set('create_cluster_start', true);
					self.controller.send('timer', true, store);
				},function(reason){
					console.log(reason.message);
					if (!Ember.isBlank(reason.message)){
						var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.controller.send('addMessage',msg);
					}
				});
				break;
			case 'hadoop_stop':
				cluster.set('hadoop_status','stop');
				cluster.save().then(function(data){
					var count = self.controller.get('count');
					var extend = Math.max(5, count);
					self.controller.set('count', extend);
					self.controller.set('create_cluster_start', true);
					self.controller.send('timer', true, store);
				},function(reason){
					console.log(reason.message);
					if (!Ember.isBlank(reason.message)){
						var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.controller.send('addMessage',msg);
					}
				});
				break;
			case 'hadoop_format':
				cluster.set('hadoop_status','format');
				cluster.save().then(function(data){
					var count = self.controller.get('count');
					var extend = Math.max(5, count);
					self.controller.set('count', extend);
					self.controller.set('create_cluster_start', true);
					self.controller.send('timer', true, store);
				},function(reason){
					console.log(reason.message);
					if (!Ember.isBlank(reason.message)){
						var msg = {'msg_type':'danger','msg_text':reason.message};
                        self.controller.send('addMessage',msg);
					}
				});
				break;
			}
		},
		
		confirmAction : function(cluster, value) {
			cluster.set('cluster_confirm_action', value);
		}	
	}
	  
	  
});