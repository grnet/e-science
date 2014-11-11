// Createcluster resource functionality
// Createcluster index route (/cluster/create url)
Orka.CreateclusterIndexRoute = Orka.RestrictedRoute.extend({

        model : function() {
                return this.store.find('createcluster', 1);
        }
});
