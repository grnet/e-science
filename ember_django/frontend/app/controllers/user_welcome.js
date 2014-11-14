// Welcome route controller
// Redirect to logout route when user press logout in welcome screen 
App.UserWelcomeController = Ember.Controller.extend({ 

  needs: 'clusterCreate',

  // Function which disables all create cluster buttons so user will have to select a role first (master/slaves) to interact with the buttons
  go_forward: function(){
    this.controllerFor('clusterCreate').set('master_enabled', false);
    this.controllerFor('clusterCreate').set('master_color', "lightblue");
    this.controllerFor('clusterCreate').set('slaves_enabled', false);
    this.controllerFor('clusterCreate').set('slaves_color', "lightblue");
    this.controllerFor('clusterCreate').set('storage_Not_Allow', true);
  },

  actions:{
    logout: function(){
      // redirect to logout
      this.transitionToRoute('user.logout');
    },

    // go to cluster/create screen
    createcluster: function(){
      this.go_forward();
      this.transitionToRoute('cluster.create');
    }    
  }
  
});
