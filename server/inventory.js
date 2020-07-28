const express = require('express');
const router = express.Router();
const child_process = require("child_process");
const fs = require('fs');
const path = require('path');

// Python virtual environment path
const envPath = path.join(__dirname, "..", "env", "Scripts", "python");

// Python scripts paths
const fetchInventoryPath = path.join(__dirname, "..", "pythonscripts", "fetchInventory.py");
const driveUploaderPath = path.join(__dirname, "..", "pythonscripts", "driveUploader.py");


// Run python script to fetch inventory
router.get('/', (req, res) => {
    const spawn = child_process.spawn;
    console.log("Running python script to fetch inventory...");
    const process = spawn(envPath, [fetchInventoryPath], {
        cwd: path.join(__dirname, "..", "pythonscripts"),
        detached: true
    });

    // Std out from python script
    process.stdout.on('data', function (data) {
        const output = data.toString();
        // console.log(output);
    });

    // On exit, read inventory from inventory.txt and send data to client
    process.on('exit', function () {
        console.log("Script ended");
        const inventoryPath = path.join(__dirname, "public", "inventory.txt");
        const array = fs.readFileSync(inventoryPath, 'utf8').split('\n');
        res.send({
            records: array
        });
    });
});


// Post request to add new inventory
router.post("/", async (req, res) => {
    // console.log(req.body);
    const cardsArray = req.body;

    // Loop through received data to populate "data" variable
    let data = '';
    for (let i = 0; i < cardsArray.length; i++) {
        const {slotNumber, cardName, cardSource, cardGrade} = cardsArray[i];
        const newCardName = slotNumber.trim() + "_" + cardName.trim() + "_" + cardSource.trim() + "_" + cardGrade.trim();
        // console.log(newCardName);
        // cardImageNames.push(newCardName);
        const cardLocation = path.join(__dirname, "public", "images", "croppedCards", "crop" + String(i) + ".png");
        // cardLocations.push(cardLocation);
        data = data + String(newCardName) + "," + String(cardLocation) + "\n";
    }

    // Write data to updateInventory.txt
    const updateInventoryPath = path.join(__dirname, "public", "updateInventory.txt");
    fs.writeFile(updateInventoryPath, data, (err) => {
        // In case of a error throw err.
        if (err) throw err;
    })


    console.log("Running python script to update inventory...");
    const spawn = child_process.spawn;
    const processTwo = spawn(envPath, [driveUploaderPath], {
        cwd: path.join("..", "pythonscripts"),
        detached: true
    });

    processTwo.stdout.on('data', function (data) {
        const output = data.toString();
        console.log(output);
    });

    processTwo.on('exit', function () {
        console.log("Uploading finished");
        res.send("Success");
    });

})

module.exports = router;

