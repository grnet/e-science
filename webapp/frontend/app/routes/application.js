// Top level route
// Using it mainly to trap events that bubble from other routes.
// Allows us to have logic to handle slower loading routes or errors in a generic way.

App.ApplicationRoute = Ember.Route.extend({
	actions : {
		loading : function(transition, route) {
			if (transition.targetName == 'cluster.create' || transition.targetName == 'vreserver.create') {
				this.set('loaderTitle', 'Computing available resources');
			} else {
				this.set('loaderTitle', 'Working');
			}
			$options = {
				title : this.get('loaderTitle'),
				fontColor : false,
				bgColor : 'transparent',
				size : 32,
				isOnly : true,
				bgOpacity : 1.0,
				imgUrl : DJANGO_STATIC_URL + "images/loading[size].gif",
				onShow : function() {
					$.loader.shown = true;
					$('.loading_wrp').find('span').addClass('text-primary big strong');
				},
				onClose : function() {
					$.loader.shown = false;
				}
			};
			$.loader.open($options);
			function loader_close() {
				$.loader.close(true);
			}
			this.router.one('didTransition', null, loader_close);
		}
	}
});
