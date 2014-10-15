App = Ember.Application.create();

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


App.HomepageController = Ember.Controller.extend({
  start: function() {
    this.transitionTo('login');
}
});

App.LoginController = Ember.Controller.extend({
//  token: '',
  actions: {
    login: function(text) {
      
      if (text) {

//	this.store.createRecord('user', {
//	  'usertoken': text
//	});

//	this.set('token', '');
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

//App.User = DS.Model.extend({
//  usertoken:  DS.attr('string')
//});
