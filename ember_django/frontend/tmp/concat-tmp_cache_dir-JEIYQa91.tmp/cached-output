eval("//# sourceURL=vendor/ember-cli/loader.js");

;eval("define(\"emberproject/app\", \n  [\"ember\",\"ember/resolver\",\"ember/load-initializers\",\"emberproject/config/environment\",\"exports\"],\n  function(__dependency1__, __dependency2__, __dependency3__, __dependency4__, __exports__) {\n    \"use strict\";\n    var Ember = __dependency1__[\"default\"];\n    var Resolver = __dependency2__[\"default\"];\n    var loadInitializers = __dependency3__[\"default\"];\n    var config = __dependency4__[\"default\"];\n\n    Ember.MODEL_FACTORY_INJECTIONS = true;\n\n    var App = Ember.Application.extend({\n      modulePrefix: config.modulePrefix,\n      podModulePrefix: config.podModulePrefix,\n      Resolver: Resolver\n    });\n\n    loadInitializers(App, config.modulePrefix);\n\n    __exports__[\"default\"] = App;\n  });//# sourceURL=emberproject/app.js");

;eval("define(\"emberproject/initializers/export-application-global\", \n  [\"ember\",\"emberproject/config/environment\",\"exports\"],\n  function(__dependency1__, __dependency2__, __exports__) {\n    \"use strict\";\n    var Ember = __dependency1__[\"default\"];\n    var config = __dependency2__[\"default\"];\n\n    function initialize(container, application) {\n      var classifiedName = Ember.String.classify(config.modulePrefix);\n\n      if (config.exportApplicationGlobal) {\n        window[classifiedName] = application;\n      }\n    };\n    __exports__.initialize = initialize;\n    __exports__[\"default\"] = {\n      name: \'export-application-global\',\n\n      initialize: initialize\n    };\n  });//# sourceURL=emberproject/initializers/export-application-global.js");

;eval("define(\"emberproject/router\", \n  [\"ember\",\"emberproject/config/environment\",\"exports\"],\n  function(__dependency1__, __dependency2__, __exports__) {\n    \"use strict\";\n    var Ember = __dependency1__[\"default\"];\n    var config = __dependency2__[\"default\"];\n\n    var Router = Ember.Router.extend({\n      location: config.locationType\n    });\n\n    Router.map(function() {\n    });\n\n    __exports__[\"default\"] = Router;\n  });//# sourceURL=emberproject/router.js");

;eval("define(\"emberproject/templates/application\", \n  [\"ember\",\"exports\"],\n  function(__dependency1__, __exports__) {\n    \"use strict\";\n    var Ember = __dependency1__[\"default\"];\n    __exports__[\"default\"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data\n    /**/) {\n    this.compilerInfo = [4,\'>= 1.0.0\'];\n    helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};\n      var buffer = \'\', stack1;\n\n\n      data.buffer.push(\"<h2 id=\'title\'>Welcome to Ember.js</h2>\\n\\n\");\n      stack1 = helpers._triageMustache.call(depth0, \"outlet\", {hash:{},hashTypes:{},hashContexts:{},contexts:[depth0],types:[\"ID\"],data:data});\n      if(stack1 || stack1 === 0) { data.buffer.push(stack1); }\n      data.buffer.push(\"\\n\");\n      return buffer;\n      \n    });\n  });//# sourceURL=emberproject/templates/application.js");

;eval("define(\"emberproject/tests/app.jshint\", \n  [],\n  function() {\n    \"use strict\";\n    module(\'JSHint - .\');\n    test(\'app.js should pass jshint\', function() { \n      ok(true, \'app.js should pass jshint.\'); \n    });\n  });//# sourceURL=emberproject/tests/app.jshint.js");

;eval("define(\"emberproject/tests/emberproject/tests/helpers/resolver.jshint\", \n  [],\n  function() {\n    \"use strict\";\n    module(\'JSHint - emberproject/tests/helpers\');\n    test(\'emberproject/tests/helpers/resolver.js should pass jshint\', function() { \n      ok(true, \'emberproject/tests/helpers/resolver.js should pass jshint.\'); \n    });\n  });//# sourceURL=emberproject/tests/emberproject/tests/helpers/resolver.jshint.js");

;eval("define(\"emberproject/tests/emberproject/tests/helpers/start-app.jshint\", \n  [],\n  function() {\n    \"use strict\";\n    module(\'JSHint - emberproject/tests/helpers\');\n    test(\'emberproject/tests/helpers/start-app.js should pass jshint\', function() { \n      ok(true, \'emberproject/tests/helpers/start-app.js should pass jshint.\'); \n    });\n  });//# sourceURL=emberproject/tests/emberproject/tests/helpers/start-app.jshint.js");

;eval("define(\"emberproject/tests/emberproject/tests/test-helper.jshint\", \n  [],\n  function() {\n    \"use strict\";\n    module(\'JSHint - emberproject/tests\');\n    test(\'emberproject/tests/test-helper.js should pass jshint\', function() { \n      ok(true, \'emberproject/tests/test-helper.js should pass jshint.\'); \n    });\n  });//# sourceURL=emberproject/tests/emberproject/tests/test-helper.jshint.js");

;eval("define(\"emberproject/tests/helpers/resolver\", \n  [\"ember/resolver\",\"emberproject/config/environment\",\"exports\"],\n  function(__dependency1__, __dependency2__, __exports__) {\n    \"use strict\";\n    var Resolver = __dependency1__[\"default\"];\n    var config = __dependency2__[\"default\"];\n\n    var resolver = Resolver.create();\n\n    resolver.namespace = {\n      modulePrefix: config.modulePrefix,\n      podModulePrefix: config.podModulePrefix\n    };\n\n    __exports__[\"default\"] = resolver;\n  });//# sourceURL=emberproject/tests/helpers/resolver.js");

;eval("define(\"emberproject/tests/helpers/start-app\", \n  [\"ember\",\"emberproject/app\",\"emberproject/router\",\"emberproject/config/environment\",\"exports\"],\n  function(__dependency1__, __dependency2__, __dependency3__, __dependency4__, __exports__) {\n    \"use strict\";\n    var Ember = __dependency1__[\"default\"];\n    var Application = __dependency2__[\"default\"];\n    var Router = __dependency3__[\"default\"];\n    var config = __dependency4__[\"default\"];\n\n    __exports__[\"default\"] = function startApp(attrs) {\n      var App;\n\n      var attributes = Ember.merge({}, config.APP);\n      attributes = Ember.merge(attributes, attrs); // use defaults, but you can override;\n\n      Router.reopen({\n        location: \'none\'\n      });\n\n      Ember.run(function() {\n        App = Application.create(attributes);\n        App.setupForTesting();\n        App.injectTestHelpers();\n      });\n\n      App.reset(); // this shouldn\'t be needed, i want to be able to \"start an app at a specific URL\"\n\n      return App;\n    }\n  });//# sourceURL=emberproject/tests/helpers/start-app.js");

;eval("define(\"emberproject/tests/router.jshint\", \n  [],\n  function() {\n    \"use strict\";\n    module(\'JSHint - .\');\n    test(\'router.js should pass jshint\', function() { \n      ok(true, \'router.js should pass jshint.\'); \n    });\n  });//# sourceURL=emberproject/tests/router.jshint.js");

;eval("define(\"emberproject/tests/test-helper\", \n  [\"emberproject/tests/helpers/resolver\",\"ember-qunit\"],\n  function(__dependency1__, __dependency2__) {\n    \"use strict\";\n    var resolver = __dependency1__[\"default\"];\n    var setResolver = __dependency2__.setResolver;\n\n    setResolver(resolver);\n\n    document.write(\'<div id=\"ember-testing-container\"><div id=\"ember-testing\"></div></div>\');\n\n    QUnit.config.urlConfig.push({ id: \'nocontainer\', label: \'Hide container\'});\n    var containerVisibility = QUnit.urlParams.nocontainer ? \'hidden\' : \'visible\';\n    document.getElementById(\'ember-testing-container\').style.visibility = containerVisibility;\n  });//# sourceURL=emberproject/tests/test-helper.js");

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
