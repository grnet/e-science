//Ember.js application for Escience login and logout functionality
//with Django backend through Django REST framework.

App = Ember.Application.create();

var attr = DS.attr;

//Global variable for Escience token
var escience_token;
this.App.set('escience_token', "null");

//User model used in our app 
App.User = DS.Model.extend({
     token: attr('string'),
     user_id: attr('number'),
     cluster: attr('number'),
    });

//Extend Application Adapter settings for Token Authentication and REST calls to /api
//Changes of global var escience_token are reflected in the Authorization header of our REST calls
App.ApplicationAdapter = DS.ActiveModelAdapter.extend({
   
   namespace: 'api',
   headers: function() {
   return { "Authorization": App.escience_token  };}.property("App.escience_token") 
   

});

//Application routes
App.Router.map(function() {
  this.route('homepage');
  this.route('login');
  this.route('welcome');
  this.route('logout');
});

//Index route (e.g localhost:port/) redirects to homepage
App.IndexRoute = Ember.Route.extend({
  redirect: function() {
    this.transitionTo('homepage');
}  
});

//Welcome user screen.
//Show user id and clusters number.
App.WelcomeRoute = Ember.Route.extend({
  
  beforeModel: function() {
                //Check if user is logged in.
                //If not, redirect to login screen.
        	if (!this.controllerFor('login').isLoggedIn()) {
            	this.transitionTo('login');
                } 
                else {
		App.set('escience_token', window.localStorage.escience_auth_token);		
		}     
    },  
  model: function() {     
        //Return user records from store.
        //Show latest record in template with latestObject.
	return this.store.find('user');   
     },

});

//Redirect to logout route when user press logout in welcome screen 
App.WelcomeController = Ember.Controller.extend({  
  logout: function(){
    this.transitionToRoute('logout');
}
});

//Redirect to login screen when user press start in homepage 
App.HomepageController = Ember.Controller.extend({
  start: function() {
    this.transitionToRoute('login');
}
});

//Login functionality happens here
App.LoginController = Ember.Controller.extend({
  token: '',
  isLoggedIn: function() {
                //Check localstorage auth token for user login status.
        	if ( window.localStorage.escience_auth_token !== 'null' ) {
            	  return true;
                }
                else {
                  return false;
                }
  },
  loginFailed: false,
  actions: {
    login: function(text) {
      var self = this;
      if (text) {
        //POST ~okeanos token to Django backend.
	var response = this.store.createRecord('user', {
	  'token': text
	}).save();
        //Handling the promise of POST request
        response.then(
        function(data) {
               //Succesfull login.
               //Set global and localStorage variables to escience token.	
               App.set('escience_token', "Token "+data._data.escience_token);
               window.localStorage.escience_auth_token = App.get('escience_token');
               //Push to store the user retrieved from Django backend.
               self.store.push('user', {
               id: 1,
               user_id: data._data.user_id,
               token: data._data.escience_token,
               cluster: data._data.cluster
	       });
               //Set the text in login screen to blank and redirect to welcome screen       
               self.set('loginFailed', false);
               self.set('token', '');
               self.transitionToRoute('welcome');             
            }, function(){
               //Failed login.
	       self.set('loginFailed', true);
	       self.set('token', '');
        });
	
      
      }
    }    
  }

});

//If user is logged in, redirect to welcome screen
App.LoginRoute = Ember.Route.extend({
  redirect: function() {
    if (this.controllerFor('login').isLoggedIn()) {
            	this.transitionTo('welcome');
                }    
}
});

//After user submits ~okeanos token, sends it to login controller
App.LoginView = Ember.View.extend({
  submit: function() {
      var text = this.get('controller.token');
      this.get('controller').send('login', text);
    }
});

//Log out user.
App.LogoutRoute = Ember.Route.extend({
  redirect: function() {
    //Send PUT request for backend logout update.
    var current_user = this.store.update('user', {'id': 1}).save();
    current_user.then(
    function(){
        //Set global var escience and localStorage token to null.
    	App.set('escience_token', "null");
        window.localStorage.escience_auth_token = App.get('escience_token');
    });
    this.transitionTo('homepage');
}  
});
