// Main application routes
App.Router.map(function() {
	this.route('homepage');
	this.route('clustermanagment');
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
	//	this.route('managment');
	});
	// Route to enforce login policy
	// other routes that require login extend this
	this.route('restricted');
});
