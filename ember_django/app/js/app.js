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
App.Createcluster = DS.Model.extend({
    vms_max: DS.attr('number'),        // maximum (limit) number of VMs 
    vms_av: DS.attr(),                  // available VMs
    cpu_max: DS.attr('number'),        // maximum CPUs
    cpu_av: DS.attr('number'),         // available CPUs
    mem_max: DS.attr('number'),        // maximum memory
    mem_av: DS.attr('number'),         // available memory     
    disk_max: DS.attr('number'),       // maximum disk space
    disk_av: DS.attr('number'),        // available disk space
    cpu_choices: DS.attr(),               // CPU choices
    mem_choices: DS.attr(),              // memory choices
    disk_choices: DS.attr(),             // disk choices
    disk_template: DS.attr(),         // storage choices
    os_choices: DS.attr()                   //Operating System choices
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
  this.resource('user', function() {
      this.route('login');
      this.route('logout');
      this.route('welcome');
  });
  this.resource('createcluster', function(){
         this.route('confirm');
     });
});

//Index route (e.g localhost:port/) redirects to homepage
App.IndexRoute = Ember.Route.extend({
  redirect: function() {
    this.transitionTo('homepage');
}  
});

//Redirect to login screen when user press start in homepage 
App.HomepageController = Ember.Controller.extend({
  start: function() {
    this.transitionToRoute('user.login');
}
});


//Welcome user screen.
//Show user id and clusters number.
App.UserWelcomeRoute = Ember.Route.extend({
  
  beforeModel: function() {
                //Check if user is logged in.
                //If not, redirect to login screen.
        	if (!this.controllerFor('user.login').isLoggedIn()) {
            	this.transitionTo('user.login');
                } 
                else {
		App.set('escience_token', window.localStorage.escience_auth_token);		
		}     
    },  
  model: function() {     
        //Return user record with id 1.
        //If user record not in store, perform a GET request
        //and get user record from server.     
     return this.store.find('user', 1);
   

     
     
 }   
});

//Redirect to logout route when user press logout in welcome screen 
App.UserWelcomeController = Ember.Controller.extend({  
  logout: function(){
    this.transitionToRoute('user.logout');
  },
  createcluster: function(){
    this.transitionToRoute('createcluster.index');
}
});


//Login functionality happens here
App.UserLoginController = Ember.Controller.extend({
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
               self.transitionToRoute('user.welcome');             
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
App.UserLoginRoute = Ember.Route.extend({
  redirect: function() {
    if (this.controllerFor('user.login').isLoggedIn()) {
            	this.transitionTo('user.welcome');
                }    
}
});

//After user submits ~okeanos token, sends it to login controller
App.UserLoginView = Ember.View.extend({
  submit: function() {
      var text = this.get('controller.token');
      this.get('controller').send('login', text);
    }
});

//Log out user.
App.UserLogoutRoute = Ember.Route.extend({
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
// access model Create_cluster
App.CreateclusterIndexRoute = Ember.Route.extend({
  
  beforeModel: function() {
                //Check if user is logged in.
                //If not, redirect to login screen.
        	if (!this.controllerFor('user.login').isLoggedIn()) {
            	this.transitionTo('user.login');
                } 
                else {
		App.set('escience_token', window.localStorage.escience_auth_token);		
		}     
    },
  model: function() {
   return this.store.find('createcluster', 1);
  }
});

// controller for flavor
App.CreateclusterIndexController = Ember.Controller.extend({
    master_enabled: true,
    slaves_enabled: false,
    Allow: true,
    cluster_name: '',
    cluster_size: 0,
    operating_system: '',
    master_color: 'lightgreen',
    slaves_color: 'lightgrey',
    
    master_cpu_selection: 0,
    slaves_cpu_selection: 0,

    total_cpu_selection: function() {
    return this.get('master_cpu_selection') + this.get('slaves_cpu_selection')*(this.get('cluster_size')-1);
     }.property('master_cpu_selection', 'slaves_cpu_selection', 'cluster_size'),

    cpu_available: function(){
    var cpu_avail = this.get('content._data.cpu_av') - this.get('total_cpu_selection');
    if (cpu_avail < 0){
      this.set('Allow', false);
      alert('You cannot assign these cpus');
      return this.get('content._data.cpu_av');
     }
    else {
     this.set('Allow', true);
     return cpu_avail;
     }
    }.property('total_cpu_selection'),

    master_mem_selection: 0,
    slaves_mem_selection: 0,

    total_mem_selection: function() {
    return this.get('master_mem_selection') + this.get('slaves_mem_selection')*(this.get('cluster_size')-1);
     }.property('master_mem_selection', 'slaves_mem_selection', 'cluster_size'),

    mem_available: function(){
    return this.get('content._data.mem_av') - this.get('total_mem_selection');
    }.property('total_mem_selection'),

    master_disk_selection: 0,
    slaves_disk_selection: 0,

    total_disk_selection: function() {
    return this.get('master_disk_selection') + this.get('slaves_disk_selection')*(this.get('cluster_size')-1);
     }.property('master_disk_selection', 'slaves_disk_selection', 'cluster_size'),
    
    disk_available: function(){
    return this.get('content._data.disk_av') - this.get('total_disk_selection');
    }.property('total_disk_selection'),

    disk_temp: 'ext_vlmc',
    actions: {
        display_master: function() {

            this.set('master_color', 'lightgreen');
            this.set('slaves_color', 'lightgrey');
            this.set('master_enabled', true);
            this.set('slaves_enabled', false);
        },
        display_slaves: function() {

            this.set('master_color', 'lightgrey');
            this.set('slaves_color', 'lightgreen');
            this.set('master_enabled', false);
            this.set('slaves_enabled', true);
        },
        // when next button is pressed
        // gotoconfirm action is triggered
        gotoconfirm: function() {
            
            // check all fields are filled
            if((this.master_cpu_selection === '') || (this.slaves_cpu_selection === '') || (this.master_mem_selection === '') ||
                (this.slaves_mem_selection === '') ||(this.master_disk_selection === '') ||(this.slaves_disk_selection === '') ||
                (this.disk_temp === '') || (this.get('cluster_name') === '')
            )
            {
                alert('Something is missing!');
            }
            else
            {
                // check if everything is allowed
    
                if( (this.get('total_cpu_selection') <= this.get("content._data.cpu_av")) &&
                    (this.get('total_mem_selection') <= this.get("content._data.mem_av")) &&
                    (this.get('total_disk_selection') <= this.get("content._data.disk_av"))
                    )
                { 
                    // redirect to confirm template
                    this.transitionTo('createcluster.confirm');
                }
                else
                {
                    alert('Requested resources unavailable!');
                }
            }
        },
        cpu_selection: function(name) {     
            if(this.master_enabled) { this.set('master_cpu_selection', name); }
            if(this.slaves_enabled) { this.set('slaves_cpu_selection', name); }
        },
        mem_selection: function(name) {     
            if(this.master_enabled) { this.set('master_mem_selection', name); }
            if(this.slaves_enabled) { this.set('slaves_mem_selection', name); }
        },        
        disk_selection: function(name) {     
            if(this.master_enabled) { this.set('master_disk_selection', name); }
            if(this.slaves_enabled) { this.set('slaves_disk_selection', name); }
        },  
        disk_template: function(name) {     
            
            this.set('disk_temp', name);
        }
  },
  master_style: function() {
    return "background-color:" + this.get('master_color');
  }.property('master_color').cacheable(),
  slaves_style: function() {
    return "background-color:" + this.get('slaves_color');
  }.property('slaves_color').cacheable()
});


App.CreateclusterConfirmRoute = Ember.Route.extend({
 
  beforeModel: function() {
                //Check if user is logged in.
                //If not, redirect to login screen.
        	if (!this.controllerFor('user.login').isLoggedIn()) {
            	this.transitionTo('user.login');
                } 
                else {
		App.set('escience_token', window.localStorage.escience_auth_token);		
		}     
    },

});

// controller for confirm
App.CreateclusterConfirmController = Ember.Controller.extend({
    // in order to have access to personalize
    needs: 'createclusterIndex',
    actions: {
        // when previous button is pressed
        // gotoflavor action is triggered
        gotoflavor: function() {
            // redirect to flavor template
            this.transitionTo('createcluster.index');
        },
        // when next button is pressed
        // gotocreate action is triggered
        gotocreate: function() {
            // do nothing for now
            
        }
    }  
});
