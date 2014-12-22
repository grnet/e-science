// Welcome user route.
// Show user id and number of clusters.
App.UserWelcomeRoute = App.RestrictedRoute.extend({
	//"user" model for the welcome route
	needs: 'userWelcome',
	beforemodel: function (){
		this.store.fetch('user', 1);
	},
	model : function() {
		$.loader.close(true);
		if (this.controllerFor('userWelcome').get('create_cluster_start') == true && this.controllerFor('userWelcome').get('output_message') == '') {
			// If transition to welcome is from create cluster button then start a loading gif until create cluster is terminated
			$options = {
				title : 'Create cluster...',
				fontColor : false,
				bgColor : 'transparent',
				size : 32,
				isOnly : true,
				bgOpacity : 1.0,
				imgUrl : "/frontend/app/images/loading[size].gif",
				onShow : function() {
					$.loader.shown = true;
					$('.loading_wrp').find('span').addClass('text-info strong');
				},
				onClose : function() {
					$.loader.shown = false;
				}
			};
			// The first option: the loader that gets all the page
			//$.loader.open($options);
			
			// Second option: the loader presented inthe place of the alert messages 			
			//$('#clusterCreationProgress').loader($options);

			// The loader is presented in the table with the User Clusters
			setTimeout(function() {
				$('#clusterCreationProgress').loader($options);
			}, 1000);
		}
		// Return user record with id 1.
		// If user record not in store, perform a GET request
		// and get user record from server.
		return this.store.fetch('user', 1);
	}
});

// if_equal_component.js script
App.IfEqualComponent = Ember.Component.extend({
  isEqual: function() {
    return this.get('param1') === this.get('param2');
  }.property('param1', 'param2')
});

App.ElseEqualComponent = App.IfEqualComponent.extend();

