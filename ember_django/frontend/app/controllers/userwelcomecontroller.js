// Welcome route controller
// Redirect to logout route when user press logout in welcome screen 
App.UserWelcomeController = Ember.Controller.extend({ 


  needs: 'createclusterIndex',

  goforward: function(){
    this.controllerFor('createclusterIndex').set('master_enabled', false);
    this.controllerFor('createclusterIndex').set('master_color', "lightblue");
    this.controllerFor('createclusterIndex').set('slaves_enabled', false);
    this.controllerFor('createclusterIndex').set('slaves_color', "lightblue");
    this.controllerFor('createclusterIndex').set('storage_Not_Allow', true);
  },

  actions:{
    logout: function(){
      this.transitionToRoute('user.logout');
    },
    createcluster: function(){
      this.goforward();
      this.transitionToRoute('createcluster.index');
    }    
  }
  
});