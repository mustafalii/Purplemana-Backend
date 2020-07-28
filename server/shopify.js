const express = require('express');
const router = express.Router();
const multer = require('multer');
const fs = require('fs');
const child_process = require("child_process");
const path = require("path");
const fsExtra = require('fs-extra')
const envPath = path.join(__dirname, "..", "env", "Scripts", "python");
const busboy = require('connect-busboy');

// Python virtual environment path
const pythonVenvPath = path.join(__dirname, "..", "env", "Scripts", "python")
// Python Shopify script
const shopifyScript = path.join(__dirname, "..", "pythonscripts", "shopify.py")


// Post request to upload product to shopify csv
router.post('/', (req, res) => {
    req.pipe(req.busboy);
    console.log("Post request for Shopify");
    var uploadPath = "";
    let formData = new Map();
    // Get field values
    req.busboy.on('field', function (fieldname, val) {
        formData.set(fieldname, val);
    });

    req.busboy.on('file', function (fieldname, file, filename) {
        console.log("Begin uploading: " + filename);

        // Upload directory
        uploadPath = path.join(__dirname, "public", "images", "shopifyImages", filename);

        let fstream = fs.createWriteStream(uploadPath);
        file.pipe(fstream);

        // On finished uploading
        fstream.on('close', function () {
            console.log(`(on close) Upload of '${filename}' finished`);
            console.log(formData);
        });
    });

    req.busboy.on('finish', function () {
        console.log("Finished Uploading");
        const shopifyProduct = path.join(__dirname, "public", "shopifyProduct.txt");
        const data =
            formData.get("handle") + "\n" +
            formData.get("title") + "\n" +
            formData.get("body") + "\n" +
            formData.get("tags") + "\n" +
            formData.get("sku") + "\n" +
            formData.get("price") + "\n" +
            formData.get("comparePrice") + "\n" +
            uploadPath + "\n" +
            formData.get("cost") + "\n";

        fs.writeFile(shopifyProduct, data, (err) => {
            if (err) throw err;
        });

        // Run pyhton script for uploading to shopify CSV
        const spawn = child_process.spawn;
        console.log("Running python script to upload to shopify CSV...");
        const process = spawn(pythonVenvPath, [shopifyScript], {
            cwd: path.join(__dirname, "..", "pythonscripts"),
            detached: true
        });

        // On receiving output from python script
        process.stdout.on('data', function (data) {
            const output = data.toString();
            console.log(output);
        });

        // On python script ending
        process.on('exit', function () {
            console.log("Uploading finished");
            res.send("Success");
        });
    });
});

module.exports = router;