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
  loginFailed: false,
  actions: {
    login: function(text) {
      
      if (text) {

	var post = this.store.createRecord('user', {
	  'token': text
	});
	
	var self=this;
	
	var onSuccess = function(post) {
	  self.transitionToRoute('welcome');
	  self.set('token', '');
	  self.set('loginFailed', false);
	};

	var onFail = function(post) {
	  // deal with the failure here
	  self.set('loginFailed', true);
	  self.set('token', '');
	};

	post.save().then(onSuccess, onFail);

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


