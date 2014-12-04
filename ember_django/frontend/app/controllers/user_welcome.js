// Welcome route controller
// Redirect to logout route when user press logout in welcome screen 
App.UserWelcomeController = Ember.Controller.extend({ 

  needs: 'clusterCreate',

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
