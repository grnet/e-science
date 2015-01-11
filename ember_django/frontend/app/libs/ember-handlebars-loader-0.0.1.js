var EmberHandlebarsLoader = {
	loadTemplates : function(templateNames) {
		templateNames.forEach(function(name) {
			$.ajax({
				url : DJANGO_STATIC_URL + "templates/" + name + ".hbs",
				async : false,
			}).done(function(template) {
				var compiledTemplate = Ember.Handlebars.precompile(template);
				Ember.TEMPLATES[name] = Ember.Handlebars.template(compiledTemplate);
				alert(template);
			});
		});
	}
};
