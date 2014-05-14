
function setBibKeys() {
  var klist = document.getElementById('bib_key_list');

  // clear key list
  var c;
  while ((c = klist.firstChild)) {
    klist.removeChild(c);
  }
 
  // get new list of keys from cur
  var http = new XMLHttpRequest;
  http.open('GET', '/bibkeys', false);
  http.send(null);
  
  // insert new children into klist 
  for (line of http.responseText.split('\n')) {
    var opt = document.createElement('option');
    opt.setAttribute('value', line);
    klist.appendChild(opt);
  }
}

function validateBibKey() {
  var klist = document.getElementById('bib_key_list');
  var input = document.getElementById('bib_key');
  
  for (option of klist.options) {
    if (option.value == input.value) {
      input.setCustomValidity('');
      return true;
    }
  }

  input.setCustomValidity('Unknown bib key.');
  return false;
}
