var express = require('express')
var fs = require('fs')
var fileUpload = require('express-fileupload');
var app = express();
var path = require('path');
var port = process.env.PORT || 3001;
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

function decompose(done){
	var decomposition = require('child_process').spawn('python3', ['decomposition.py']);
	fs.readFile('uploads/uploaded_ttsp.txt', function(err, data) {
		if (err) {
			return console.log(err);
		}
		console.log(data);
		decomposition.stdin.write(data);
		// End data write
		decomposition.stdin.end();
		decomposition.on('close', function(){
			done();
		});
	});
}

app.use(express.static('public'))

app.use(fileUpload());

app.post('/upload', function(req, res) {
    var sampleFile;
 
    if (!req.files) {
        res.send('No files were uploaded.');
        return;
    }
 
    sampleFile = req.files.sampleFile;
    sampleFile.mv('uploads/uploaded_ttsp.txt', function(err) {
        if (err) {
            res.status(500).send(err);
        }
        else {
        	decompose(function(err){
        		return res.redirect('/');
        	});
        	
        }
    });
});


//routes
app.get('/', function(req, res) {
	res.sendFile(__dirname + '/index.html');
});

app.listen(3001, () => {
	console.log('Server started at http://localhost:' + port);
});