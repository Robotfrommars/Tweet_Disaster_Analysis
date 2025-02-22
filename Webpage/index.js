var express = require('express');
var router = express.Router();
var mongoose = require('mongoose');

// MongoDB Atlas Connection
const MONGO_URI = "mongodb+srv://armonhadjimani:ND_analysis@cluster0.dqx5o.mongodb.net/disaster_tweets?retryWrites=true&w=majority";

mongoose.connect(MONGO_URI)
  .then(() => console.log("Connected to MongoDB Atlas"))
  .catch(err => console.error("MongoDB Connection Error:", err));

// Define Tweet Schema
const tweetSchema = new mongoose.Schema({
  user: String,
  text: String,
  query: String,
  timestamp: String
});

const Tweet = mongoose.model("Tweet", tweetSchema);

// GET home page & Fetch Tweets
router.get('/', async function(req, res, next) {
  try {
    const tweets = await Tweet.find().sort({ timestamp: -1 }).limit(50);
    res.render('index', { title: 'Bluesky Tweets', tweets });
  } catch (error) {
    res.status(500).send("Error fetching tweets.");
  }
});

module.exports = router;
