// Application routes
App.Router.map(function() {
        this.route('homepage');
        this.resource('user', function() {
		// /user/login
                this.route('login');
                // /user/logout
		this.route('logout');
		// /user/welcome
                this.route('welcome');
        });
        this.resource('createcluster', {
                path : "/cluster/create"
        }, function() {
		// /cluster/create/confirm
                this.route('confirm', {
                        path : "/confirm"
                });
        });
        // Route to enforce login policy
	// other routes that require login extend this
        this.route('restricted');
});
