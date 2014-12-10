// Welcome user route.
// Show user id and number of clusters.
App.UserWelcomeRoute = App.RestrictedRoute.extend({
	//"user" model for the welcome route
	needs: 'userWelcome',
	model : function() {
		$.loader.close(true);
		if (this.controllerFor('userWelcome').get('create_cluster_start') == true) {
			// If transition to welcome is from create cluster button then start a loading gif until create cluster is terminated
			$options = {
				title : 'Creating cluster...',
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
			$.loader.open($options);
		}
		// Return user record with id 1.
		// If user record not in store, perform a GET request
		// and get user record from server.
		return this.store.find('user', 1);
	}
});
