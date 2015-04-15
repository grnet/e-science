// Main application routes
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
	this.resource('cluster', function() {
		// /cluster/create
		this.route('create');
		this.route('management', { path: "/:usercluster.cluster_name" });
	});
	// Route to enforce login policy
	// other routes that require login extend this
	this.route('restricted');
});
