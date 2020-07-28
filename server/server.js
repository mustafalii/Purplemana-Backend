const express = require('express');
const cors = require("cors");
const path = require("path");
const busboy = require("connect-busboy");
const inventory = require(path.join(__dirname, '/inventory'));
const upload = require(path.join(__dirname, '/upload'));
const shopify = require(path.join(__dirname, '/shopify'));
const app = express();
app.use(express.json());
app.use(express.static(__dirname + '/public'));

// Insert the busboy middle-ware
app.use(busboy({
    highWaterMark: 2 * 1024 * 1024, // Set 2MiB buffer
}));

// Define cors options
const whiteList = ['http://localhost:3000'];
const corsOptions = {
    origin: function (origin, callback) {
        if (whiteList.indexOf(origin) != -1 || origin == undefined) {
            callback(null, true);
        } else {
            console.log(origin);
            callback(new Error('Not allowed by CORS'));
        }
    }
}

// Pass cors options
app.use(cors(corsOptions));


// Home Page
app.get('/', (req, res) => {
    res.send("Home get request");
});


// Routes
app.use('/inventory', inventory);
app.use('/upload', upload);
app.use('/shopify', shopify);


// LISTENING ON PORT 5000
const PORT = 5000;
app.listen(PORT, () => {
    console.log('Listening at ' + PORT);
});


