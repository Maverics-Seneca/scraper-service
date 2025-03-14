require('dotenv').config(); // Load environment variables from .env file

const express = require('express');
const cors = require('cors'); // Import cors
const axios = require('axios');
const admin = require('firebase-admin');
const app = express();
const PORT = 4006; // Change as needed

// Initialize Firebase
const serviceAccount = JSON.parse(Buffer.from(process.env.FIREBASE_CREDENTIALS, 'base64').toString('utf8'));
admin.initializeApp({ credential: admin.credential.cert(serviceAccount) });
const db = admin.firestore();

// Middleware
app.use(cors({
    origin: 'http://middleware:3001', // Allow requests from middleware
    credentials: true, // Allow cookies to be sent
}));

// Define the new API endpoint
app.get('/api/medicine/details', async (req, res) => {
    const { patientId } = req.query;

    if (!patientId) {
        return res.status(400).json({ error: "Missing patientId query parameter" });
    }

    try {
        // Call the existing API to get medicines
        const response = await axios.get(`http://localhost:4002/api/medicine/get?patientId=${patientId}`);

        // Extract only medicine names
        const medicineNames = response.data.map(med => med.name);

        if (!medicineNames || medicineNames.length === 0) {
            return res.status(400).json({ error: "No medicine names found" });
        }

        // Call Firestore query function
        const data = await queryMedicinesBatch(medicineNames);

        // Send response as JSON
        res.status(200).json(data);
    } catch (error) {
        console.error('Error fetching medicines:', error.message);
        res.status(500).json({ error: 'Failed to fetch medicines' });
    }
});

async function queryMedicinesBatch(medicineNames) {
    const collectionRef = db.collection("drugsInfo");
    let results = [];

    // Firestore `in` supports up to 10 values per query
    for (let i = 0; i < medicineNames.length; i += 10) {
        const batch = medicineNames.slice(i, i + 10);
        const snapshot = await collectionRef.where("name", "in", batch).get();

        snapshot.forEach(doc => results.push(doc.data()));
    }
    return results;
}

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
