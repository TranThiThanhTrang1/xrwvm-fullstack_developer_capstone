const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');
const path = require('path');
const app = express();
const port = 3030;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// Load data from JSON
const reviewsData = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'reviews.json'), 'utf8'));
const dealershipsData = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'dealerships.json'), 'utf8'));

// Connect to MongoDB
mongoose.connect("mongodb://mongo_db:27017/", { dbName: 'dealershipsDB' })
  .then(() => console.log("MongoDB connected"))
  .catch(err => console.error("MongoDB connection error:", err));

// Models
const Reviews = require('./review');
const Dealerships = require('./dealership');

// Initialize MongoDB data
(async () => {
  try {
    await Reviews.deleteMany({});
    await Reviews.insertMany(reviewsData.reviews);
    console.log("Reviews initialized");

    await Dealerships.deleteMany({});
    await Dealerships.insertMany(dealershipsData.dealerships);
    console.log("Dealerships initialized");
  } catch (error) {
    console.error("Error initializing data:", error);
  }
})();

// Routes
app.get('/', (req, res) => res.send("Welcome to the Mongoose API"));

// Fetch all dealers
app.get('/fetchDealers', async (req, res) => {
  try {
    const dealers = await Dealerships.find();
    res.json(dealers);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealers' });
  }
});

// Fetch dealers by state
app.get('/fetchDealers/state/:state', async (req, res) => {
  try {
    const state = req.params.state;
    const dealers = await Dealerships.find({ state });
    res.json(dealers);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealers by state' });
  }
});

// Fetch dealer by id
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const id = Number(req.params.id);
    const dealer = await Dealerships.findOne({ id });
    if (!dealer) return res.status(404).json({ message: 'Dealer not found' });
    res.json(dealer);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealer' });
  }
});

// Fetch all reviews
app.get('/fetchReviews', async (req, res) => {
  try {
    const allReviews = await Reviews.find();
    res.json(allReviews);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching reviews' });
  }
});

// Fetch reviews by dealer id
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const dealerId = Number(req.params.id);
    const dealerReviews = await Reviews.find({ dealership: dealerId });
    res.json(dealerReviews);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching reviews by dealer' });
  }
});

// Insert review
app.post('/insert_review', async (req, res) => {
  try {
    const data = req.body;
    const lastReview = await Reviews.findOne().sort({ id: -1 });
    const newId = lastReview ? lastReview.id + 1 : 1;

    const review = new Reviews({
      id: newId,
      name: data.name,
      dealership: data.dealership,
      review: data.review,
      purchase: data.purchase,
      purchase_date: data.purchase_date,
      car_make: data.car_make,
      car_model: data.car_model,
      car_year: data.car_year,
    });

    const savedReview = await review.save();
    res.json(savedReview);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

// Start server
app.listen(port, () => console.log(`Server running at http://localhost:${port}`));
