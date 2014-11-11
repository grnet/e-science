// Createcluster confirm route (/cluster/create/confirm url)
Orka.CreateclusterConfirmRoute = Orka.RestrictedRoute.extend({

        model : function() {
                // Return user record with id 1.
                // If user record not in store, perform a GET request
                // and get user record from server.
                return this.store.find('user', 1);

        }
});
