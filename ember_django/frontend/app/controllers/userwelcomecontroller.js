// Welcome route controller
// Redirect to logout route when user press logout in welcome screen 
App.UserWelcomeController = Ember.Controller.extend({ 


  needs: 'createclusterIndex',

  // Function which disable all flavor buttons so user will have to selecet a role frist (master/slaves) to interact with the buttons
  go_forward: function(){
    this.controllerFor('createclusterIndex').set('master_enabled', false);
    this.controllerFor('createclusterIndex').set('master_color', "lightblue");
    this.controllerFor('createclusterIndex').set('slaves_enabled', false);
    this.controllerFor('createclusterIndex').set('slaves_color', "lightblue");
    this.controllerFor('createclusterIndex').set('storage_Not_Allow', true);
  },

  actions:{
    logout: function(){
      // redirect to logout
      this.transitionToRoute('user.logout');
    },

    // go to crete/cluster screen
    createcluster: function(){
      this.go_forward();
      this.transitionToRoute('createcluster.index');
    }    
  }
  
});