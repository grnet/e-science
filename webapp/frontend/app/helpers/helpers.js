// formatDate handlebars helper
// use as {{ formatDate date format='dateformat' }}
var DateFormats = {
    shortdate : 'YYYY-MM-DD', // 2015-12-30
    shortdatemon : 'DD MMM YYYY', // 15 Mth 2015
    shortdatetime : 'ddd, DD MMM YYYY HH:mm:ss' //Day, 15 Mth 2015 23:59:59
};
Ember.Handlebars.helper('formatDate', function(date, options) {
    var format = 'shortdate';
    if (options.hash.format) {
        format = options.hash.format;
    }
    return new Ember.Handlebars.SafeString(moment(date).format(DateFormats[format]));
});

// use as {{ printBigNum num separator='.' decimal=','}} separator and decimal are optional
Ember.Handlebars.helper('printBigNum', function(num, options) {
    var separator = '.';
    var decimal = ',';
    if (options.hash.separator) {
        separator = options.hash.separator;
    }
    if (options.hash.decimal) {
        decimal = options.hash.decimal;
    }
    num = num.toString(); // convert to string if not already passed as such
    var arrparts = num.split(decimal); // split to whole and decimal parts
    var result = arrparts[0];
    // decimal
    var remainder = arrparts[1];
    // fraction
    var fraction = "";
    if ( typeof (result) != "undefined") {
        // reverse the digits. regexp works from left to right.
        for ( i = result.length - 1; i >= 0; i--)
            fraction += result.charAt(i);
        // add separators. but undo the trailing one, if there
        fraction = fraction.replace(/(\d{3})/g, "$1" + separator);
        if (fraction.slice(-separator.length) == separator)
            fraction = fraction.slice(0, -separator.length);
        result = "";
        // reverse again to get back the number
        for ( i = fraction.length - 1; i >= 0; i--)
            result += fraction.charAt(i);
        // add the fraction back in, if it was there
        if ( typeof (remainder) != "undefined" && remainder.length > 0)
            result += decimal + remainder;
    }
    return result;
});

// if equal helper
// checks equality of two arguments
Ember.Handlebars.registerHelper('ifeq', function(a, b, options) {
    return Ember.Handlebars.bind.call(options.contexts[0], a, options, true, function(result) {
        return result === b;
    });
});

/**
Example:
  {{#eachidx bar in foo}}
    {{index}} - {{bar}}
  {{/#eachidx}}
handlebars values:
{{index}} //0-based index
{{index_1}} //1-based index
{{first}} {{last}} {{even}} {{odd}} //booleans
*/
Ember.Handlebars.registerHelper('eachidx', function eachHelper(path, options) {
var $ = Ember.$;
var keywordName = 'item';
var fn;
  
  if (arguments.length === 4) {
    // Process arguments #eachidx foo in bar
    Ember.assert('If you pass more than one argument to the eachidx helper, it must be in the form #eachidx foo in bar', arguments[1] === 'in');
    Ember.assert(arguments[0] +' is a reserved word in #eachidx', $.inArray(arguments[0], ['index', 'index+1', 'even', 'odd']));

    keywordName = arguments[0];
    options = arguments[3];
    path = arguments[2];
    options.hash.keyword = keywordName;
    
    if (path === '') { 
      path = 'this'; 
    }
  } else if (arguments.length === 1) {
    // Process arguments #earchIndexed bar
    options = path;
    path = 'this';
  }

  // Wrap the callback function in our own that sets the index value
  fn = options.fn;
  function eachFn() {
    var keywords = arguments[1].data.view._keywords,
        view = arguments[1].data.view,
        index = view.contentIndex,
        list = view._parentView.get('content') || [],
        len = list.length || list.get('length');

    // Set indexes
    keywords['index'] = index;
    keywords['index_1'] = index + 1;
    keywords['first'] = (index === 0);
    keywords['last'] = (index + 1 === len);
    keywords['even'] = (index % 2 === 0);
    keywords['odd'] = !keywords['even'];
    arguments[1].data.keywords = keywords;

    return fn.apply(this, arguments);
  }
  options.fn = eachFn; 

  // Render
  options.hash.dataSourceBinding = path;
  if (options.data.insideGroup && !options.hash.groupedRows && !options.hash.itemViewClass) {
    new Ember.Handlebars.GroupedEach(this, path, options).render();
  } else {
    return Ember.Handlebars.helpers.collection.call(this, Ember.Handlebars.EachView, options);
  }
}); 
