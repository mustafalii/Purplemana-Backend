const express = require('express');
const router = express.Router();
const fs = require('fs');
const child_process = require("child_process");
const path = require("path");
const fsExtra = require('fs-extra')
const busboy = require('connect-busboy');

// Python virtual environment path
const pythonVenvPath = path.join(__dirname, "..", "env", "Scripts", "python")


// Testing purposes
router.get('/', (req, res) => {
    console.log("Get request to upload");
});

// On delete request, delete all files from scannedCards & detectedCards directory
router.delete('/', (req, res) => {
    fsExtra.emptyDirSync(path.join(__dirname, 'public', 'images', 'scannedCards'));
    fsExtra.emptyDirSync(path.join(__dirname, 'public', 'images', 'detectedCards'));
})


// Post request to /upload to handle detection of cards
router.post('/', async (req, res) => {

    var files = 0, finished = false;
    req.busboy.on('file', function (fieldname, file, filename) {
        console.log("Begin uploading: " + filename);
        ++files;
        const uploadPath = path.join(__dirname, "public", "images", "scannedCards", filename);
        let fstream = fs.createWriteStream(uploadPath);
        file.pipe(fstream);

        // See upload progress
        file.on('readable', () => {
            let chunk;
            while (null !== (chunk = file.read())) {
                console.log(`Received ${chunk.length} bytes of data`);
            }
        });

        // On finish of file upload
        fstream.on('close', function () {
            --files;
            console.log(`(on close) Upload of '${filename}' finished`);
            console.log("(on close) # Files Left: ", files);

            if (files === 0 && finished) {
                console.log("(on close) ALL UPLOADING FINISHED");
                runPythonScript((slotLetter, detectedCards) => {
                    console.log(slotLetter, detectedCards);
                    res.send({
                        files: detectedCards,
                        slotLetter: slotLetter
                    });
                    fsExtra.emptyDirSync(path.join(__dirname, 'public', 'images', 'scannedCards'));
                });
            }
        });

    });

    req.busboy.on('finish', function () {
        console.log("Busyboy finish called");
        finished = true;
    });

    req.pipe(req.busboy);
})
;


function runPythonScript(callback) {
    let slotLetter = 'No Slot Letter Detected';
    let detectedCards = [];

    // Spawn new process
    const spawn = child_process.spawn;
    console.log("Running python script...");
    const pythonScriptPath = path.join(__dirname, "..", "pythonscripts", "autocrop.py");
    const process = spawn(pythonVenvPath, [pythonScriptPath], {
        cwd: path.join(__dirname, "..", "pythonscripts"),
        detached: true
    });

    // Update slot letter
    process.stdout.on('data', function (data) {
        const output = data.toString();
        const outputArray = output.split("\r\n");
        outputArray.forEach(word => {
            if (word.length === 1) {
                slotLetter = word;
            }
        })
    });

    // On script exit, read each file from detectedCards directory and send response
    process.on('exit', function () {
        console.log("Python script ended");
        const directoryPath = path.join(__dirname, 'public', 'images', 'detectedCards');
        fs.readdir(directoryPath, async function (err, files) {
            console.log("This should print after python script");

            if (err) {
                return 'Unable to scan directory: ' + err;
            }

            files.forEach(function (file) {
                const cardsScan = file;
                detectedCards.push("http://localhost:5000/images/detectedCards/" + cardsScan);
                console.log("Adding card scan: " + cardsScan);

                // Callback function when detectedCards topHalf & bottomHalf of both images
                if (detectedCards.length === 4) {
                    callback(slotLetter, detectedCards);
                }
            });
        });
    });
}


module.exports = router;