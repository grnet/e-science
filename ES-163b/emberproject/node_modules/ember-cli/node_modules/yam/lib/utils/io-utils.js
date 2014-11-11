'use strict';

var fs = require('fs-extra');

var exists = function exists(path) {
  return fs.existsSync(path);
};

var stripComments = function stripComments(string) {
  string = string || "";

  string = string.replace(/\/\*(?:(?!\*\/)[\s\S])*\*\//g, "");
  string = string.replace(/\/\/\s\S.+/g, ""); // Everything after '//'

  return string;
};

var readFile = function readFile(path) {
  var result;

  try {
    var contents = fs.readFileSync(path, { encoding: 'utf8' });

    result = JSON.parse(stripComments(contents));
  } catch(e) {
    result = {};
  }

  return result;
};

module.exports.readFile = readFile;
module.exports.exists   = exists;
