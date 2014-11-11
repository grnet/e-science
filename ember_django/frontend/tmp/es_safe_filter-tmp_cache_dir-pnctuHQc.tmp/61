//import Ember from 'ember';
//import config from './config/environment';

// Application routes
Orka.Router.map(function() {
        this.route('homepage');
        this.resource('user', function() {
                this.route('login');
                this.route('logout');
                this.route('welcome');
        });
        this.resource('createcluster', {
                path : "/cluster/create"
        }, function() {
                this.route('confirm', {
                        path : "/confirm"
                });
        });
        // Route to enforce login policy
        this.route('restricted');
});

// Index route (e.g localhost:port/) redirects to homepage
Orka.IndexRoute = Ember.Route.extend({
        redirect : function() {
                this.transitionTo('homepage');
        }
});

// Every route that requires loggedIn user will extend this route
Orka.RestrictedRoute = Ember.Route.extend({
        beforeModel : function() {
                // Check if user is logged in.
                // If not, redirect to login screen.
                if (!this.controllerFor('user.login').isLoggedIn()) {
                        this.transitionTo('user.login');
                } else {
                        Orka.set('escience_token', window.localStorage.escience_auth_token);
                }
        }
});
// Welcome functionality
// Welcome user route.
// Show user id and clusters number.
Orka.UserWelcomeRoute = Orka.RestrictedRoute.extend({

        model : function() {
                // Return user record with id 1.
                // If user record not in store, perform a GET request
                // and get user record from server.
                return this.store.find('user', 1);
        }
});

// Login route
// If user is logged in, redirect to welcome screen
Orka.UserLoginRoute = Ember.Route.extend({
        redirect : function() {
                if (this.controllerFor('user.login').isLoggedIn()) {
                        this.transitionTo('user.welcome');
                }
        }
});

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

// Createcluster resource functionality
// Createcluster index route (/cluster/create url)
Orka.CreateclusterIndexRoute = Orka.RestrictedRoute.extend({

        model : function() {
                return this.store.find('createcluster', 1);
        }
});

// Createcluster confirm route (/cluster/create/confirm url)
Orka.CreateclusterConfirmRoute = Orka.RestrictedRoute.extend({

        model : function() {
                // Return user record with id 1.
                // If user record not in store, perform a GET request
                // and get user record from server.
                return this.store.find('user', 1);

        }
});


//export default Orka.IndexRoute;
//export default Orka.RestrictedRoute;
//export default Orka.UserWelcomeRoute;
//export default Orka.UserLoginRoute;
//export default Orka.UserLogoutRoute;
//export default Orka.CreateclusterIndexRoute;
//export default Orka.CreateclusterConfirmRoute;
