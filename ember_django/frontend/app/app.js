// Ember application for Escience. Extending login/logout functionality
// with choice of create cluster details from a form.
// Django backend communicating with Ember through Django REST framework.

window.App = Ember.Application.create({
	VERSION: '0.1',
    // Basic logging
    LOG_TRANSITIONS: true,
    LOG_ACTIVE_GENERATION: true,
    LOG_VIEW_LOOKUPS: true,
    // LOG_RESOLVER: true,
    rootElement: 'body',
  	ready: function() {
    
  }
});

App.attr = DS.attr;

// Global variable for Escience token
// for authorization purposes
var escience_token;
App.set('escience_token', "null");
