// Home Page controller
App.HomepageController = Ember.Controller.extend({
	STATIC_URL : DJANGO_STATIC_URL,
	APP_VERSION : App.VERSION,
	spawned_clusters: '0',
	active_clusters: '0',
	spawned_vres: '0',
	active_vres: '0',
	news_items : [],
	orkaImages : []
});