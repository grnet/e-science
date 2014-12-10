module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
        all: {
            files: [{
                expand: true,
                cwd: 'ember_django/frontend/app/',
                src: ['**/*.js', '!**/*.min.js', '!libs/**/*'],
                dest: 'ember_django/frontend/app/',
                ext: '.js'
            }]
        }
    }
  });

  // Load the plugin that provides the "uglify" task.
  grunt.loadNpmTasks('grunt-contrib-uglify');

  // Default task(s).
  grunt.registerTask('default', ['uglify']);

};