var express = require('express')
var fs = require('fs')
var app = express();
var path = require('path');
var port = process.env.PORT || 3000;
var assert = require('assert');
var PythonShell = require('python-shell');

var synthetic = new PythonShell('synthetic_ttsp.py');
var decomposition = require('child_process').spawn('python3', ['decomposition.py']);

synthetic.end(function(err) {
	if (err) throw err;
	console.log('finished');
	fs.readFile('synthetic_ttsp.txt', function(err, data) {
		if (err) {
			return console.log(err);
		}
		console.log(data);
		decomposition.stdin.write(data);
		// End data write
		decomposition.stdin.end();
	});
});

app.use(express.static('public'))

//routes
app.get('/', function(req, res) {
	res.sendFile(__dirname + '/index.html');
});

app.listen(3000, () => {
	console.log('Server started at http://localhost:' + port);
});