// Logout route
// Log out user.
Orka.UserLogoutRoute = Ember.Route.extend({
        redirect : function() {
                // Send PUT request for backend logout update.
                var current_user = this.store.update('user', {
                        'id' : 1
                }).save();
                current_user.then(function() {
                        // Set global var escience and localStorage token to null when put is successful.
                        Orka.set('escience_token', "null");
                        window.localStorage.escience_auth_token = Orka.get('escience_token');
                }, function() {
                        // Set global var escience and localStorage token to null when put fails.
                        Orka.set('escience_token', "null");
                        window.localStorage.escience_auth_token = Orka.get('escience_token');
                });
                this.transitionTo('homepage');

        }
});
