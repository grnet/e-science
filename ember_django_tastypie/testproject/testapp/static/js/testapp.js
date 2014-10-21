(function($, undefined ) {
    Testapp = Ember.Application.create();

    Testapp.ApplicationAdapter = DS.DjangoTastypieAdapter.extend({});
    Testapp.ApplicationSerializer = DS.DjangoTastypieSerializer.extend({});

    var attr = DS.attr;

    Testapp.Tester = DS.Model.extend({
        uuid: attr('string'),
    });

    
    Testapp.Router.map(function() {
        this.route('testers-list');
    });
    
    Testapp.Router.map(function() {
        this.route('add-tester');
    });
    
    Testapp.IndexRoute = Ember.Route.extend({
        redirect: function() {
            this.transitionTo('add-tester');
        }
    });
    
    Testapp.TestersListRoute = Ember.Route.extend({
        model: function() {
            return this.store.find('tester');
        }
    });
    
    
    
    
    
    Testapp.AddTesterController = Ember.Controller.extend({
        tester: '',
        actions: {
            saveTester: function(text) {
                if (text) {
                    this.store.createRecord('tester', {'uuid': text}).save();
		    this.set('tester', '');
                    this.transitionToRoute('testers-list');
                }
            }
        }
    });

    Testapp.AddTesterView = Ember.View.extend({
        submit: function() {
            var text = this.get('controller.tester');
            this.get('controller').send('saveTester', text);
        }
    });
    
    
}(jQuery));