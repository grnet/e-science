// Ember application for e-science.
window.App = Ember.Application.create({
	VERSION: '0.1',
    // Basic logging
    LOG_TRANSITIONS: true,
    // LOG_TRANSITIONS_INTERNAL: true,
    LOG_ACTIVE_GENERATION: true,
    LOG_VIEW_LOOKUPS: true,
    LOG_BINDINGS: true,
    // LOG_RESOLVER: true,
    rootElement: 'body',
  	ready: function() {

  }
});

App.attr = DS.attr;

// Global variable for e-science token
// for authorization purposes
var escience_token;
App.set('escience_token', "null");


