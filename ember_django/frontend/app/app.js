// Ember application for Escience. Extending login/logout functionality
// with choice of create cluster details from a form.
// Django backend communicating with Ember through Django REST framework.

window.App = Ember.Application.create({
    // Basic logging
    LOG_TRANSITIONS : true
});

App.attr = DS.attr;

// Global variable for Escience token
// for authorization purposes
var escience_token;
App.set('escience_token', "null");