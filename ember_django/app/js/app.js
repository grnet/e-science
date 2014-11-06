// Ember.js application for Escience. Extending login/logout functionality
// with choice of create cluster details from a form.
// Django backend communicating with Ember through Django REST framework.

Orka = Ember.Application.create({
	LOG_TRANSITIONS : true
});

// Global variable for Escience token
var escience_token;
Orka.set('escience_token', "null");

// Extend Application Adapter settings for Token Authentication and REST calls to /api
// Changes of global var escience_token are reflected in the Authorization header of our REST calls
Orka.ApplicationAdapter = DS.ActiveModelAdapter.extend({

	namespace : 'api',
	headers : function() {
		return {
			"Authorization" : Orka.escience_token
		};
	}.property("Orka.escience_token")

});

