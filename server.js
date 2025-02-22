const express = require('express');
const app = express();
const PORT = 4003;

app.use(express.json());

app.listen(PORT, () => {
    console.log(`Scraper Service running on port ${PORT}`);
});