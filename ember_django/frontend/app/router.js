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
