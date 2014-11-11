// Ember.js application for Escience. Extending login/logout functionality
// with choice of create cluster details from a form.
// Django backend communicating with Ember through Django REST framework.

//import Ember from 'ember';
//import Resolver from 'ember/resolver';
//import loadInitializers from 'ember/load-initializers';
//import config from './config/environment';

//Ember.MODEL_FACTORY_INJECTIONS = true;

window.App = Ember.Application.create({
    // from enber-cli
//    modulePrefix: config.modulePrefix,
//    podModulePrefix: config.podModulePrefix,
//    Resolver: Resolver
    // from enber-cli

    LOG_TRANSITIONS : true
});

App.attr = DS.attr;

// Global variable for Escience token
var escience_token;
App.set('escience_token', "null");

/* 
 The store holds data loaded from the server (i.e. records). 
 Routes and controllers can query the store for records. 
 If a given record is called for the first time, then the store tells the adapter to load it over the network. 
 Then, the store caches it for the next time you ask for it. 
 */
// Extend Application Adapter settings for Token Authentication and REST calls to /api
// Changes of global var escience_token are reflected in the Authorization header of our REST calls

// from ember-cli
//loadInitializers(App, config.modulePrefix);
//export default App;
// from ember-cli