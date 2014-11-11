//import Ember from 'ember';
//import config from './config/environment';

// Application routes
App.Router.map(function() {
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

//export default App.IndexRoute;
//export default App.RestrictedRoute;
//export default App.UserWelcomeRoute;
//export default App.UserLoginRoute;
//export default App.UserLogoutRoute;
//export default App.CreateclusterIndexRoute;
//export default App.CreateclusterConfirmRoute;
