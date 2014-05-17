function setBibKeys(url) {
  var klist = document.getElementById('key_list');

  // clear key list
  var c;
  while ((c = klist.firstChild)) {
    klist.removeChild(c);
  }
 
  // get new list of keys from cur
  var http = new XMLHttpRequest;
  http.open('GET', url, false);
  http.send();
  
  // insert new children into klist
  if (http.status == 200) {
    for (var line of http.responseText.split('\n')) {
      var opt = document.createElement('option');
      opt.setAttribute('value', line);
      klist.appendChild(opt);
    }
  }
}

function validateBibKey(input) {
  var klist = document.getElementById('key_list');
  
  for (var option of klist.options) {
    if (option.value == input.value) {
      input.setCustomValidity('');
      return true;
    }
  }

  input.setCustomValidity('Unknown bib key.');
  return false;
}

function validateNym(input) {
  input.setCustomValidity('');
  return true;
}

function addNymInput(button) {
  // make new nym input
  var input = document.createElement('input');
  input.setAttribute('name', 'nym');
  input.setAttribute('type', 'text');
  input.onblur = function(event) { if (this.value) validateNym(this); };

  var td = document.createElement('td');
  td.appendChild(input);

  // move the button down a row
  var bi_row = button.parentNode.parentNode;
  button.parentNode.removeChild(button);
  td.appendChild(button);

  var tr = document.createElement('tr');
  tr.appendChild(document.createElement('td'));
  tr.appendChild(td);

  bi_row.parentNode.insertBefore(tr, bi_row.nextElementSibling);
}

function validateVNF() {
  var key = document.getElementById('key');
  var result = validateBibKey(key);

  var nyms = document.getElementsByName("nym");
  for (var input of nyms) {
    result &= validateNym(input);
  }

  return result;
}
