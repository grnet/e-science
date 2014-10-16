App = Ember.Application.create();

var attr = DS.attr;

App.User = DS.Model.extend({
     token: attr('string'),
     user_id: attr('number'),
     cluster: attr('number'),
    });

App.UserAdapter = DS.RESTAdapter.extend({
  namespace: 'api'
});


App.Router.map(function() {
  this.route('homepage');
  this.route('login');
  this.route('welcome');
  this.route('notauthorized');
  this.route('logout');
});

App.IndexRoute = Ember.Route.extend({
  redirect: function() {
    this.transitionTo('homepage');
}  
});

App.LogoutRoute = Ember.Route.extend({
  redirect: function() {
    this.transitionTo('homepage');
}  
});

App.WelcomeRoute = Ember.Route.extend({
        model: function() {
            return this.store.all('user');
        }
    });

App.HomepageController = Ember.Controller.extend({
  start: function() {
    this.transitionTo('login');
}
});

App.LoginController = Ember.Controller.extend({
  token: '',
  actions: {
    login: function(text) {
      
      if (text) {

	this.store.createRecord('user', {
	  'token': text
	}).save();

	this.set('token', '');
	this.transitionToRoute('welcome');
      }
    }    
  }
});

App.LoginView = Ember.View.extend({
  submit: function() {
      var text = this.get('controller.token');
      this.get('controller').send('login', text);
    }
});


App.WelcomeController = Ember.Controller.extend({
  logout: function() {
    this.transitionTo('logout');
}
});


