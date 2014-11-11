// create an Ember application
App = Ember.Application.create();

App.ApplicationAdapter = DS.FixtureAdapter;

// status model... to be retrieved from the backend
App.Status = DS.Model.extend({
    vms_max: DS.attr('number'),         // maximum (limit) number of VMs
    vms_av: DS.attr(),                  // available VMs
    cpu_max: DS.attr('number'),         // maximum CPUs
    cpu_av: DS.attr('number'),          // available CPUs
    mem_max: DS.attr('number'),         // maximum memory
    mem_av: DS.attr('number'),          // available memory
    disk_max: DS.attr('number'),        // maximum disk space
    disk_av: DS.attr('number'),         // available disk space
    cpu_p: DS.attr(),                   // CPU choices
    mem_p: DS.attr(),                   // memory choices
    disk_p: DS.attr(),                  // disk choices
    disk_template: DS.attr(),            // storage choices
    os_p: DS.attr()                     // OS choices    
});

App.Status.reopenClass({
  FIXTURES: [
    { 
        id: 1,
        vms_max: 10,
        vms_av: [1,2,3,4,5,6],
        cpu_max: 8,
        cpu_av: 4,
        mem_max: 8192,
        mem_av: 2048,
        disk_max: 100,
        disk_av: 20,
        cpu_p: [1,2,4,8],
        mem_p: [512,1024,2048,4096,8192],
        disk_p: [5,10,20,40,60,80,100],
        disk_template: ['Standard','Archipelago'],
        os_p: ['Debian','Linux','Ubuntu']        
    }
  ]
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

// for the flavor route
// access model status
App.FlavorRoute = Ember.Route.extend({
  model: function() {
    return this.store.find('status');
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
                if( (this.mastercpuselection+this.slavescpuselection <= this.get("content.lastObject.cpu_av")) &&
                    (this.mastermemselection+this.slavesmemselection <= this.get("content.lastObject.mem_av")) &&
                    (this.masterdiskselection+this.slavesdiskselection <= this.get("content.lastObject.disk_av"))
                    )
                {
                    // read the value for the cluster name
                    this.totalcpuselection=this.mastercpuselection+this.slavescpuselection;
                    this.totalmemselection=this.mastermemselection+this.slavesmemselection;
                    this.totaldiskselection=this.masterdiskselection+this.slavesdiskselection;
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
