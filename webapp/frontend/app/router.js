// Main application routes
App.Router.map(function() {
	this.route('homepage');

	this.resource('help', function() {
		// /help/images
		this.route('images');
		// /help/vreimages
		this.route('vreimages');
		// /help/experiments
		this.route('experiments');
	});

});
