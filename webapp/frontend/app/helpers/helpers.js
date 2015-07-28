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

// if equal helper
// checks equality of two arguments
Ember.Handlebars.registerHelper('ifeq', function(a, b, options) {
    return Ember.Handlebars.bind.call(options.contexts[0], a, options, true, function(result) {
        return result === b;
    });
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
