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


//export default Orka.IndexRoute;
//export default Orka.RestrictedRoute;
//export default Orka.UserWelcomeRoute;
//export default Orka.UserLoginRoute;
//export default Orka.UserLogoutRoute;
//export default Orka.CreateclusterIndexRoute;
//export default Orka.CreateclusterConfirmRoute;
