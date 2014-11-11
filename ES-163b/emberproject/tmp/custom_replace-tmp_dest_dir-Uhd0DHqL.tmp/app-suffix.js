/* jshint ignore:start */

define('emberproject/config/environment', ['ember'], function(Ember) {
  var prefix = 'emberproject';
/* jshint ignore:start */

try {
  var metaName = prefix + '/config/environment';
  var rawConfig = Ember['default'].$('meta[name="' + metaName + '"]').attr('content');
  var config = JSON.parse(unescape(rawConfig));

  return { 'default': config };
}
catch(err) {
  throw new Error('Could not read config from meta tag with name "' + metaName + '".');
}

/* jshint ignore:end */


});

if (runningTests) {
  require('emberproject/tests/test-helper');
} else {
  require('emberproject/app')['default'].create({"LOG_ACTIVE_GENERATION":true,"LOG_VIEW_LOOKUPS":true});
}

/* jshint ignore:end */
