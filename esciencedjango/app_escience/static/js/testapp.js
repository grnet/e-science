
    Testapp = Ember.Application.create();

    var attr = DS.attr;

    Testapp.User = DS.Model.extend({
        token: attr('string'),
        user_id: attr('number'),
        cluster: attr('number'),
    });

    
    Testapp.Router.map(function() {
  	this.route("users");
  	this.route("login");
    // new Marios entry below
    this.route('logout');
    //end new entry
    });
    
    Testapp.IndexRoute = Ember.Route.extend({
        redirect: function() {
            this.transitionTo('login');
        }
    });
    
    Testapp.UsersRoute = Ember.Route.extend({
        model: function() {
            return this.store.all('user');
        }
    });

    // new entry
    Testapp.LogoutRoute = Ember.Route.extend({
    redirect: function() {
    this.transitionTo('login');
    }  
    });
    // 

    Testapp.LoginController = Ember.Controller.extend({
        user: '',
        actions: {
            saveUser: function(text) {
                if (text) {
                    this.store.createRecord('user', {'token': text}).save();
		    this.set('user', '');
                    this.transitionToRoute('users');
                }
            }
        }
    });


    //new below
    Testapp.UsersController = Ember.Controller.extend({
        logout: function() {
        this.transitionTo('logout');
        }
    });
    // end new

    Testapp.LoginView = Ember.View.extend({
        submit: function() {
            var text = this.get('controller.user');
            this.get('controller').send('saveUser', text);
        }
    });

    
    
