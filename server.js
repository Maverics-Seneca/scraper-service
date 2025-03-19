// Import required modules
const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors'); // Import cors
const axios = require('axios');
const admin = require('firebase-admin');

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();
const PORT = 4006; // Change as needed

// Initialize Firebase
const serviceAccount = JSON.parse(Buffer.from(process.env.FIREBASE_CREDENTIALS, 'base64').toString('utf8'));
admin.initializeApp({ credential: admin.credential.cert(serviceAccount) });
const db = admin.firestore();

// Middleware setup
app.use(cors({
    origin: 'http://middleware:3001', // Allow requests from middleware
    credentials: true, // Allow cookies to be sent
}));

// Utility Functions

/**
 * Queries Firestore for medicine details in batches.
 * Firestore `in` supports up to 10 values per query.
 * @param {string[]} medicineNames - Array of medicine names to query.
 * @returns {Promise<Array>} - Array of medicine details from Firestore.
 */
async function queryMedicinesBatch(medicineNames) {
    const collectionRef = db.collection("drugsInfo");
    let results = [];

    // Process medicine names in batches of 10
    for (let i = 0; i < medicineNames.length; i += 10) {
        const batch = medicineNames.slice(i, i + 10);
        const snapshot = await collectionRef.where("name", "in", batch).get();

        snapshot.forEach(doc => results.push(doc.data()));
    }
    return results;
}

// API Endpoints

/**
 * Get detailed information about medicines for a specific patient.
 * @route GET /api/medicine/details
 * @param {string} patientId - The ID of the patient to fetch medicine details for.
 */
app.get('/api/medicine/details', async (req, res) => {
    const { patientId } = req.query;

    // Input validation
    if (!patientId) {
        console.error('Missing patientId query parameter');
        return res.status(400).json({ error: "Missing patientId query parameter" });
    }

    try {
        // Call the existing API to get medicines
        const response = await axios.get('http://middleware:3001/medicine/get', {
            params: { patientId }
        });

        // Extract only medicine names
        const medicineNames = response.data.map(med => med.name);

        if (!medicineNames || medicineNames.length === 0) {
            console.error('No medicine names found for patientId:', patientId);
            return res.status(400).json({ error: "No medicine names found" });
        }

        console.log('Medicine names retrieved:', medicineNames); // Log medicine names

        // Call Firestore query function
        const data = await queryMedicinesBatch(medicineNames);

        console.log('Medicine details retrieved:', data); // Log medicine details

        // Send response as JSON
        res.status(200).json(data);
    } catch (error) {
        console.error('Error fetching medicines:', error.message);
        res.status(500).json({ error: 'Failed to fetch medicines', details: error.message });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});