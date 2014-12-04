emq.globalize();
App.rootElement='#ember-testing';
setResolver(Ember.DefaultResolver.create({namespace: App}));
App.setupForTesting();
App.injectTestHelpers();