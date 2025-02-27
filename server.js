const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');

const app = express();
const PORT = 4006;

app.use(express.json());

// Scrape medicine details
app.get('/scrape/:medicine', async (req, res) => {
    const { medicine } = req.params;
    const searchUrl = `https://www.drugs.com/search.php?searchterm=${encodeURIComponent(medicine)}`;

    try {
        const response = await axios.get(searchUrl);
        const $ = cheerio.load(response.data);

        // Extract details (modify selectors based on the site structure)
        let results = [];
        $('.ddc-media-title').each((i, el) => {
            results.push($(el).text().trim());
        });

        if (results.length === 0) {
            return res.status(404).json({ error: "No medicine details found" });
        }

        res.json({ medicine, details: results });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: "Failed to scrape data" });
    }
});

// Health Check
app.get('/health', (req, res) => {
    res.json({ status: "Scraper Service is running" });
});

app.listen(PORT, () => {
    console.log(`Scraper Service running on port ${PORT}`);
});
