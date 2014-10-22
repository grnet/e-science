// create an Ember application
App = Ember.Application.create();

// define possible routes
App.Router.map(function() {
  this.route('flavor');
  this.route('personalize');
  this.route('confirm');
});

// for the index route
// start/redirect to the flavor template
App.IndexRoute = Ember.Route.extend({
  redirect: function() {
    this.transitionTo('flavor');
  }
});

// controller for flavor
App.FlavorController = Ember.Controller.extend({
  actions: {
    // when next button is pressed
    // gotopersonalize action is triggered
    gotopersonalize: function() {
        // redirect to personalize template
        this.transitionTo('personalize');
    }
  }  
});

// controller for personalize
App.PersonalizeController = Ember.Controller.extend({
    clname: '',
    actions: {
        // when previous button is pressed
        // gotoflavor action is triggered
        gotoflavor: function() {
            // redirect to flavor template
            this.transitionTo('flavor');
        },
        // when next button is pressed
        // gotoconfirm action is triggered
        gotoconfirm: function() {
            
            // read the value for the cluster name
            this.clname=this.get('clustername');

            // redirect to confirm template
            this.transitionTo('confirm');
        }
  }  
});

// controller for confirm
App.ConfirmController = Ember.Controller.extend({
    // in order to have access to personalize
    needs: "personalize",
    actions: {
        // when previous button is pressed
        // gotopersonalize action is triggered
        gotopersonalize: function() {
            // redirect to personalize template
            this.transitionTo('personalize');
        },
        // when next button is pressed
        // gotocreate action is triggered
        gotocreate: function() {
            // do nothing for now
            
        }
    }  
});
