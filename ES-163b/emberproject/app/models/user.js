// User model used in our app
Orka.User = DS.Model.extend({
	token : DS.attr('string'),      //okeanos token
	user_id : DS.attr('number'),    // user_id in backend database
	cluster : DS.attr('number')     // number of user clusters
}); 