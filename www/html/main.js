
function doStart() {
	const form = document.getElementById('startForm').value

	var messageText = document.getElementById('log').value
	messageText = messageText.split('\n')[0]
	document.getElementById('startMessage').value = messageText

	form.submit()
}

function populateStorage() {
	  localStorage.setItem('log', document.getElementById('log').value);

	  assignLogFromStorage();
}

function assignLogFromStorage() {
	  var currentLogValue = localStorage.getItem('log');

	  document.getElementById('log').value = currentLogValue;
}

var textForm = document.getElementById('log');

if(!localStorage.getItem('log')) {
	populateStorage();
} else {
	assignLogFromStorage();
}
textForm.onchange = populateStorage;

