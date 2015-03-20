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

App.TextFileUpload = Ember.TextField.extend({
  type: 'file',
  attributeBindings: ['name'],
  change: function (evt) {
    var files = evt.target.files;
    if (!files.length) {
      alert('Please select a file!');
      return;
    }
    var file = files[0];
    var reader = new FileReader();
    var core_site;	
    // If we use onloadend, we need to check the readyState.
    reader.onload = (function(theFile) {
    	 return function(e) {
          // Render thumbnail.
          alert('ok');
          core_site = e.target.result;
          console.log(core_site);
        };
      })(file);
    return reader.readAsText(file);
    }	
});


