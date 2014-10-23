// create an Ember application
App = Ember.Application.create();

// status model... to be retrieved from the backend
App.Status = DS.Model.extend({
    vms_max: DS.attr('number'),        // maximum (limit) number of VMs 
    vms_av: DS.attr('number'),         // available VMs
    cpu_max: DS.attr('number'),        // maximum CPUs
    cpu_av: DS.attr('number'),         // available CPUs
    mem_max: DS.attr('number'),        // maximum memory
    mem_av: DS.attr('number'),         // available memory     
    disk_max: DS.attr('number'),       // maximum disk space
    disk_av: DS.attr('number'),        // available disk space
    cpu_poss: DS.attr('string'),       // CPU choices
    mem_poss: DS.attr('string'),       // memory choices
    disk_poss: DS.attr('string'),      // disk choices
    disk_template: DS.attr('string')   // storage choices
});

// define possible routes
App.Router.map(function() {
  this.route('flavor');
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
    clname: '',
    actions: {
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
