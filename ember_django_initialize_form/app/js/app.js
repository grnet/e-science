//Ember.js application for Escience. Extending login/logout functionality 
//with choice of create cluster details from a form.
//Django backend communicating with Ember through Django REST framework.

App = Ember.Application.create();

var attr = DS.attr;

//Global variable for Escience token
var escience_token;
this.App.set('escience_token', "null");

//User model used in our app 
App.User = DS.Model.extend({
     token: attr('string'),     //okeanos token
     user_id: attr('number'),   // user_id in backend database
     cluster: attr('number')    // number of user clusters
    });

//Model used for retrieving create cluster information 
App.Status = DS.Model.extend({
    vms_max: DS.attr('number'),        // maximum (limit) number of VMs 
    vms_av: DS.attr(),                  // available VMs
    cpu_max: DS.attr('number'),        // maximum CPUs
    cpu_av: DS.attr('number'),         // available CPUs
    mem_max: DS.attr('number'),        // maximum memory
    mem_av: DS.attr('number'),         // available memory     
    disk_max: DS.attr('number'),       // maximum disk space
    disk_av: DS.attr('number'),        // available disk space
    cpu_poss: DS.attr(),               // CPU choices
    mem_poss: DS.attr(),              // memory choices
    disk_poss: DS.attr(),             // disk choices
    disk_template: DS.attr(),         // storage choices
    os_p: DS.attr()                   //Operating System choices
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
  this.route('flavor');
  this.route('confirm');
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
     
     return this.store.find('user', 1);
   

     
     
 }   
});

//Redirect to logout route when user press logout in welcome screen 
App.WelcomeController = Ember.Controller.extend({  
  logout: function(){
    this.transitionToRoute('logout');
  },
  createcluster: function(){
    this.transitionToRoute('flavor');
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
        	if ( window.localStorage.escience_auth_token != 'null' && !Ember.isEmpty(window.localStorage.escience_auth_token) && window.localStorage.escience_auth_token !== 'undefined') {
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
        //Set global var escience and localStorage token to null when put is successful.
    	App.set('escience_token', "null");
        window.localStorage.escience_auth_token = App.get('escience_token');
    }, function(){
     //Set global var escience and localStorage token to null when put fails.
    	App.set('escience_token', "null");
        window.localStorage.escience_auth_token = App.get('escience_token'); 
    });
    this.transitionTo('homepage');
}  
});

// for the flavor route
// access model status
App.FlavorRoute = Ember.Route.extend({
  
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
   return this.store.find('status', 1);
  }
});

// controller for flavor
App.FlavorController = Ember.Controller.extend({
    masterenabled: true,
    slavesenabled: false,
    clname: '',
    clsize: '',
    os: '',
    mastercolor: 'lightgreen',
    slavescolor: 'lightgrey',
    mastercpuselection: '',
    slavescpuselection: '',
    totalcpuselection: '',
    mastermemselection: '',
    slavesmemselection: '',
    totalmemselection: '',
    masterdiskselection: '',
    slavesdiskselection: '',
    totaldiskselection: '',
    disktemp: '',
    actions: {
        displaymaster: function() {

            this.set('mastercolor', 'lightgreen');
            this.set('slavescolor', 'lightgrey');
            this.set('masterenabled', true);
            this.set('slavesenabled', false);
        },
        displayslaves: function() {

            this.set('mastercolor', 'lightgrey');
            this.set('slavescolor', 'lightgreen');
            this.set('masterenabled', false);
            this.set('slavesenabled', true);
        },
        // when next button is pressed
        // gotoconfirm action is triggered
        gotoconfirm: function() {
            
            // check all fields are filled
            if((this.mastercpuselection === '') || (this.slavescpuselection === '') || (this.mastermemselection === '') ||
                (this.slavesmemselection === '') ||(this.masterdiskselection === '') ||(this.slavesdiskselection === '') ||
                (this.disktemp === '') || (this.get('clustername') === '')
            )
            {
                alert('Something is missing!');
            }
            else
            {
                // check if everything is allowed
                if( (this.mastercpuselection+this.slavescpuselection*(this.get('clustersize')-1) <= this.get("content._data.cpu_av")) &&
                    (this.mastermemselection+this.slavesmemselection*(this.get('clustersize')-1) <= this.get("content._data.mem_av")) &&
                    (this.masterdiskselection+this.slavesdiskselection*(this.get('clustersize')-1) <= this.get("content._data.disk_av"))
                    )
                {
                    // read the value for the cluster name
                    this.totalcpuselection=this.mastercpuselection+this.slavescpuselection*(this.get('clustersize')-1);
                    this.totalmemselection=this.mastermemselection+this.slavesmemselection*(this.get('clustersize')-1);
                    this.totaldiskselection=this.masterdiskselection+this.slavesdiskselection*(this.get('clustersize')-1);
                    this.clname=this.get('clustername'); 
                    this.clsize=this.get('clustersize');
                    this.os=this.get('operatingsystem'); 
                    // redirect to confirm template
                    this.transitionTo('confirm');
                }
                else
                {
                    alert('Requested resources unavailable!');
                }
            }
        },
        cpuselection: function(name) {     
            if(this.masterenabled) { this.set('mastercpuselection', name); }
            if(this.slavesenabled) { this.set('slavescpuselection', name); }
        },
        memselection: function(name) {     
            if(this.masterenabled) { this.set('mastermemselection', name); }
            if(this.slavesenabled) { this.set('slavesmemselection', name); }
        },        
        diskselection: function(name) {     
            if(this.masterenabled) { this.set('masterdiskselection', name); }
            if(this.slavesenabled) { this.set('slavesdiskselection', name); }
        },  
        disktemplate: function(name) {     
            
            this.set('disktemp', name);
        }
  },
  masterstyle: function() {
    return "background-color:" + this.get('mastercolor');
  }.property('mastercolor').cacheable(),
  slavesstyle: function() {
    return "background-color:" + this.get('slavescolor');
  }.property('slavescolor').cacheable()
});


App.ConfirmRoute = Ember.Route.extend({
 
  beforeModel: function() {
                //Check if user is logged in.
                //If not, redirect to login screen.
        	if (!this.controllerFor('login').isLoggedIn()) {
            	this.transitionTo('login');
                } 
                else {
		App.set('escience_token', window.localStorage.escience_auth_token);		
		}     
    }

});

// controller for confirm
App.ConfirmController = Ember.Controller.extend({
    // in order to have access to personalize
    needs: "flavor",
    actions: {
        // when previous button is pressed
        // gotoflavor action is triggered
        gotoflavor: function() {
            // redirect to flavor template
            this.transitionTo('flavor');
        },
        // when next button is pressed
        // gotocreate action is triggered
        gotocreate: function() {
            // do nothing for now
            
        }
    }  
});
