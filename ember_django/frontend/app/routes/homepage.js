App.HomepageRoute = Ember.Route.extend({
	// model for homepage route (Cluster Statistics)
	model : function(params) {
		var that = this;
		// Perform GET request for cluster statistics
		this.store.fetch('homepage', 1).then(function(homepage) {

			that.controller.set('spawned_clusters', homepage.get('spawned_clusters'));
			that.controller.set('active_clusters', homepage.get('active_clusters'));
			return homepage;
		}, function(reason) {
			console.log(reason.message);
		});
	},

	actions : {
		didTransition : function(transition) {
			var that = this;
			// Perform GET request for images
			this.store.fetch('okeanosimage', {}).then(function(images) {
				console.log(images.get('content'));
			}, function(reason) {
				console.log(reason.message);
			});
		}
	}
});
