var express = require('express');
var router = express.Router();
var mongoose = require('mongoose');
require("dotenv").config();
let mKey =process.env.MAP_KEY;
// MongoDB Atlas Connection
const MONGO_URI = process.env.MDB_URL;

mongoose.connect(MONGO_URI)
  .then(() => console.log("Connected to MongoDB Atlas"))
  .catch(err => console.error("MongoDB Connection Error:", err));

// Define Tweet Schema
const tweetSchema = new mongoose.Schema({
  user: String,
  text: String,
  query: String,
  timestamp: String,
  latitude: Number,
  longitude: Number,
  disaster_type: String
});

const Tweet = mongoose.model("Tweet", tweetSchema);


// GET home page & Fetch Tweets
router.get('/', async function(req, res, next) {
  try {
    const tweets = await Tweet.find({disaster_type: { $in: ["tornado", "hurricane","earthquake","flood","wildfire","blizzard","haze","meteor"] } }).sort({ timestamp: -1 }).limit(500);
    let tCount = await Tweet.find({disaster_type: { $in: ["tornado"] } }).countDocuments();
    let hCount = await Tweet.find({disaster_type: { $in: ["hurricane"] } }).countDocuments();
    let eCount = await Tweet.find({disaster_type: { $in: ["earthquake"] } }).countDocuments();
    let fCount = await Tweet.find({disaster_type: { $in: ["flood"] } }).countDocuments();
    let wCount = await Tweet.find({disaster_type: { $in: ["wildfire"] } }).countDocuments();
    let bCount = await Tweet.find({disaster_type: { $in: ["blizzard"] } }).countDocuments();
    let zCount = await Tweet.find({disaster_type: { $in: ["haze"] } }).countDocuments();
    let mCount = await Tweet.find({disaster_type: { $in: ["meteor"] } }).countDocuments();
    let barData=[tCount,hCount,eCount,fCount,wCount,bCount,zCount,mCount];
    console.log(tCount);
    res.render('index', { title: 'Bluesky Tweets', tweets, mKey, barData  });
    
  } catch (error) {
    res.status(500).send("Error fetching tweets.");
  }
});

module.exports = router;
