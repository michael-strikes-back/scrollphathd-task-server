
var textForm = document.getElementById('log');

if(!localStorage.getItem('log')) {
	populateStorage();
} else {
	assignLogFromStorage();
}

function populateStorage() {
	  localStorage.setItem('log', document.getElementById('log').value);

	  assignLogFromStorage();
}

function assignLogFromStorage() {
	  var currentLogValue = localStorage.getItem('log');

	  document.getElementById('log').value = currentLogValue;
}

textForm.onchange = populateStorage;

