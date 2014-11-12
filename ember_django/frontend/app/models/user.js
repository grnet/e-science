attr = App.attr;
// User model used in our app
App.User = DS.Model.extend({
	token : attr('string'),      //okeanos token
	user_id : attr('number'),    // user_id in backend database
	cluster : attr('number')     // number of user clusters
}); 
