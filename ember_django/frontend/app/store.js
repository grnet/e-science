// Extend Application Adapter settings for Token Authentication and REST calls to /api
// Changes of global var escience_token are reflected in the Authorization header of our REST calls

App.ApplicationAdapter = DS.ActiveModelAdapter.extend({

	namespace : 'api',
	headers : function() {
		return {
			"Authorization" : App.escience_token
		};
	}.property("App.escience_token")

}); 