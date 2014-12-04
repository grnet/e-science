moduleFor('controller:application', 'Unit Tests - Controllers', {
	setup: function(){
		visit('/');
	},
	teardown: function(){
		App.reset();
		// phantomjs seems to keep localstorage cache between tests, leads to false positives
    	localStorage.clear(); 
	}
});

test('home_controller_starts_in_logged_out_state', function() {
  expect(1);

  var ctrl = this.subject();

  equal(ctrl.get('loggedIn'), false);
});
