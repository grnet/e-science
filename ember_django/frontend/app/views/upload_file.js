App.TextFileUpload = Ember.TextField.extend({
  type: 'file',
  attributeBindings: ['name'],
  change: function (evt) {
    var files = evt.target.files;
    if (!files.length) {
      alert('Please select a file!');
      return;
    }
    var file = files[0];
    var reader = new FileReader();
    var core_site;	
    // If we use onloadend, we need to check the readyState.
    reader.onload = (function(theFile) {
    	 return function(e) {
          // Render thumbnail.
          alert('File output is in console.');
          uploadFile = e.target.result;
          console.log(uploadFile);
		//return theFile.sendAction('action', uploadFile);
        };
      })(file);
    return reader.readAsText(file);
    }	
});
