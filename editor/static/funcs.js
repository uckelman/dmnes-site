function setBibKeys() {
  var klist = document.getElementById('key_list');

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
  var klist = document.getElementById('key_list');
  var input = document.getElementById('key');
  
  for (option of klist.options) {
    if (option.value == input.value) {
      input.setCustomValidity('');
      return true;
    }
  }

  input.setCustomValidity('Unknown bib key.');
  return false;
}

function addNymInput(button_input) {
  // make new nym input
  var input = document.createElement('input');
  input.setAttribute('name', 'nym');
  input.setAttribute('type', 'text');

  var td = document.createElement('td');
  td.appendChild(input);

  // move the button down a row
  var bi_row = button_input.parentNode.parentNode;
  button_input.parentNode.removeChild(button_input);
  td.appendChild(button_input);

  var tr = document.createElement('tr');
  tr.appendChild(document.createElement('td'));
  tr.appendChild(td);

  bi_row.parentNode.insertBefore(tr, bi_row.nextElementSibling);
}
