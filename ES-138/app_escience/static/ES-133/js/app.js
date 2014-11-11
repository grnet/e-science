App = Ember.Application.create();

var attr = DS.attr;
var escience_token;
this.App.set('escience_token', "null");

App.User = DS.Model.extend({
     token: attr('string'),
     user_id: attr('number'),
     cluster: attr('number'),
    });

App.ApplicationAdapter = DS.ActiveModelAdapter.extend({
   
   namespace: 'api',
   headers: function() {
   return { "Authorization": App.escience_token  };}.property("App.escience_token") 
   

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
    this.transitionToRoute('homepage');
}  
});

App.WelcomeRoute = Ember.Route.extend({
        model: function() {
             
	     var current_user = this.store.find('user');
             return current_user;
	    //var current_user = this.store.find('user').then(
	    //function(current_user) {
            //console.log(current_user.content);
	    //return current_user.content;
            //});
            //var current_user_2 = this.store.push('user', current_user);
            
        }
    });


App.HomepageController = Ember.Controller.extend({
  start: function() {
    this.transitionToRoute('login');
}
});

App.LoginController = Ember.Controller.extend({
  token: '',
  actions: {
    login: function(text) {
      var self = this;
      if (text) {

	var response = this.store.createRecord('user', {
	  'token': text
	}).save();
        response.then(
        function() {		
               App.set('escience_token', "Token "+response.content._data.escience_token);
               self.set('token', '');
               self.transitionToRoute('welcome');             
            }, function(){     
                self.set('loginFailed', true);
                self.set('token', '');
        });
	
      
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


//App.WelcomeController = Ember.Controller.extend({
//  logout: function() {
//    this.transitionToRoute('homepage');
//}
//});

App.WelcomeController = Ember.Controller.extend({
  logout: function() {
      
    var self=this;
    
    var current_user = this.store.update('user', {'id':1}).save();
    current_user.then(
        function() {
            App.set('escience_token', "null");
            
        });
    self.transitionTo('homepage');
}

});
