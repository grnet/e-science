/* 
 The store holds data loaded from the server (i.e. records). 
 Routes and controllers can query the store for records. 
 If a given record is called for the first time, then the store tells the adapter to load it over the network. 
 Then, the store caches it for the next time you ask for it. 
*/

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

// For fixtures
// App.ApplicationAdapter = DS.FixtureAdapter;