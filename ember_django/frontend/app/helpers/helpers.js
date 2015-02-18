// formatDate handlebars helper
// use as {{ formatDate date format='dateformat' }}

var DateFormats = {  
  shortdate: 'YYYY-MM-DD', // 2015-12-30
  shortdatetime: 'ddd,DD MMM YYYY HH:mm:ss' //Day,15 Mon 2015 23:59:59
};

Ember.Handlebars.helper('formatDate', function(date, options) {  
  var format = 'shortdate';
  if (options.hash.format) {
    format = options.hash.format;
  }
  return new Ember.Handlebars.SafeString(moment(date).format(DateFormats[format]));
});