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
		// /help/personalorka
		this.route('personalorka');
	});
	this.resource('about', function() {
        // /about/orka
        this.route('orka');
        // /about/faq
        this.route('faq');
    });
});
