function setDatalist(dlist, url) {
  var lastmod = dlist.getAttribute('data-lastmod') || new Date(0).toUTCString();

  // get new list from url
  var http = new XMLHttpRequest;
  http.open('GET', url, false);
  http.setRequestHeader('If-Modified-Since', lastmod);
  http.send();
  
  if (http.status != 304) {
    // clear datalist on any response except 304 Not Modified
    var c;
    while ((c = dlist.firstChild)) {
      dlist.removeChild(c);
    }
  }

  if (http.status == 200) {
    // insert new children into datalist
    for (var line of http.responseText.split('\n')) {
      var opt = document.createElement('option');
      opt.setAttribute('value', line);
      dlist.appendChild(opt);
    }

    // update the date of last modification
    lastmod = http.getResponseHeader('Last-Modified');
    dlist.setAttribute('data-lastmod', lastmod);
  }
}

function validateAgainstDatalist(value, dlist) {
  for (var option of dlist.options) {
    if (option.value == value) {
      return true;
    }
  }
  return false;
}

function setBibKeys(url) {
  setDatalist(document.getElementById('key_list'), url);
}

function validateBibKey(input) {
  var klist = document.getElementById('key_list');
  var result = validateAgainstDatalist(input.value, klist);
  input.setCustomValidity(result ? '' : 'Unknown bib key.');
  return result;
}

function setNymKeys(input, url) {
  nlist_id = input.getAttribute('list');
  setDatalist(document.getElementById(nlist_id), url);
}

function validateNym(input) {
  var result = true;
  if (input.value) {
    nlist_id = input.getAttribute('list');
    var nlist = document.getElementById(nlist_id);
    result = validateAgainstDatalist(input.value, nlist);
  }
  input.setCustomValidity(result ? '' : 'Unknown nym.');
  return result;
}

function addNymInput(button) {
  this.max_nym = ++this.max_nym || 1; // first additional nym is 1
  var copy_nym_id = 'nym_' + this.max_nym;
  var dlist_id = 'nym_list_' + this.max_nym;

  // make new nym input
  var orig_nym = document.getElementById('nym_0');
  var copy_nym = orig_nym.cloneNode(false);
  copy_nym.setAttribute('id', copy_nym_id);
  copy_nym.setAttribute('list', dlist_id);
  copy_nym.value = '';

  // make datalist for new nym
  var dlist = document.createElement('datalist');
  dlist.setAttribute('id', dlist_id);

  var td = document.createElement('td');
  td.appendChild(copy_nym);
  td.appendChild(dlist);

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

  // We must actually return true or false for onsubmit,
  // not just something coercible. Strange but true.
  return result == true;
}
