// Home Page controller
App.HomepageController = Ember.Controller.extend({
	STATIC_URL : DJANGO_STATIC_URL,
	spawned_clusters: '0',
	active_clusters: '0',
	news_items : [],
	orkaImages : []
});