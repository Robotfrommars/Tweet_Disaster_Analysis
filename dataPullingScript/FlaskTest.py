from flask import Flask, request, jsonify, after_this_request
from tweet_analysis import runscripts
import spacy
import joblib
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
import time

from pymongo import MongoClient, ReplaceOne
from typing import List
from datetime import datetime, timedelta, timezone

from models import BlueskyPost
from atproto import Client
import config
import re
import emoji

class DataManager:
    def __init__(self):
        print("Connecting to MongoDB Atlas")
        try:
            self.client = MongoClient(
                config.MONGO_URI,
                tls=True,
                tlsAllowInvalidCertificates=True
            )
            self.db = self.client[config.DB_NAME]
            self.collection = self.db["tweets"]
            print("Connected to MongoDB Atlas successfully!")
        except Exception as e:
            print(f"MongoDB Connection Error: {e}")
            exit()

    def get_all_posts(self) -> List[BlueskyPost]:
        return [BlueskyPost(**doc) for doc in self.collection.find()]

    def add_bluesky_posts(self, posts: List[BlueskyPost]):
        if not posts:
            return

        operations = [
            ReplaceOne({"user": post.user, "text": post.text}, post.dict(), upsert=True)
            for post in posts
        ]
        result = self.collection.bulk_write(operations)
        print(f"Inserted/Updated {result.upserted_count} posts.")

    def is_duplicate(self, post: BlueskyPost) -> bool:
        return self.collection.find_one({"user": post.user, "text": post.text}) is not None

    def delete_old_posts(self):
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=5)
        result = self.collection.delete_many({"createdAt": {"$lt": cutoff_date}})
        print(f"Deleted {result.deleted_count} old posts from MongoDB.")

SEARCH_TERMS = ["tornado", "hurricane", "earthquake", "flood", "wildfire", "blizzard", "haze", "meteor"]
MAX_DOWNLOADS = 10

def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = emoji.replace_emoji(text, replace='')
    return text.strip()

class BlueskyFetcher:
    def __init__(self, data_manager: DataManager):
        print("Logging into Bluesky API")
        self.client = Client()
        self.login()
        self.data_manager = data_manager

    def login(self):
        try:

            self.client.login(config.USERNAME, config.PASSWORD)
            print("Bluesky login successful!")
        except Exception as e:
            print(f"Bluesky login failed: {e}")
            exit()

    def search_bluesky_posts(self, cursor, query):
        try:
            response = self.client.app.bsky.feed.search_posts({
                'q': query,
                'lang': 'en',
                'limit': 10, #
                'cursor': cursor
            })

            if not response or not response.posts:
                print(f"No results found for {query}")
                return [], None

            print(f"Found {len(response.posts)} posts for {query}")
            results = []

            for post in response.posts:
                cleaned_text = clean_text(post.record.text)

                formatted_post = BlueskyPost(
                    user=post.author.handle,
                    text=cleaned_text,
                    query=query,
                    timestamp=post.record.created_at,
                    location=[],
                    latitude=None,
                    longitude=None
                )

                if not self.data_manager.is_duplicate(formatted_post):
                    results.append(formatted_post)

            next_cursor = response.cursor if hasattr(response, 'cursor') else None
            return results, next_cursor

        except Exception as e:
            print(f"Error searching posts: {e}")
            return [], None

    def fetch_posts(self):
        self.data_manager.delete_old_posts()
        all_posts = []
        for query in SEARCH_TERMS:
            downloaded_count = 0
            cursor = None
            while downloaded_count < MAX_DOWNLOADS:
                print(f"Searching posts for {query} at index {downloaded_count}")
                posts, cursor = self.search_bluesky_posts(cursor, query)
                if not posts:
                    break
                all_posts.extend(posts)     ##
                downloaded_count += len(posts)
                if downloaded_count >= MAX_DOWNLOADS or not cursor:
                    break
        return all_posts


nlp = spacy.load("en_core_web_sm")

geolocator = Nominatim(user_agent="tweet-disaster-locator")
location_cache = {}

def update_post_locations_on_list(posts):
    print('Adding location information to posts')
    for post in posts:
        add_location(post)  ##
    return posts

def add_location(post):
    try:
        print(f"\nProcessing post text: {post.text}")
        print(f"[debug] location field before: {post.location}")

        if post.text is not None and len(post.text) > 0 and len(post.location) == 0:
            locations = extract_locations(post.text)
            print(f"[debug] Extracted locations: {locations}")
            post.location = locations

            post.latitude = None
            post.longitude = None

            if locations:
                coordinates = get_coordinates(locations[0])
                if coordinates:
                    post.latitude = coordinates["lat"]
                    post.longitude = coordinates["lng"]
                    print(f"[debug] Added coordinates for '{locations[0]}': {coordinates}")
                else:
                    print(f"[debug] couldn't geocode location: {locations[0]}")
            else:
                print("[debug] No location found in text.")
    except Exception as e:
        print(f"Error adding location data: {e}")


def extract_locations(text):
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    return list(set(locations))

def get_coordinates(location_name):
    if location_name in location_cache:
        return location_cache[location_name]

    try:

        location = geolocator.geocode(location_name)
        if location:
            coords = {"lat": location.latitude, "lng": location.longitude}
            location_cache[location_name] = coords
            return coords
    except GeocoderServiceError as e:
        print(f"Geocoder error for '{location_name}': {e}")
    except Exception as e:
        print(f"error while geocoding '{location_name}': {e}")

    return None

class DisasterPredictor():
    def __init__(self):
        self.vectorizer = joblib.load('../tfidf_vectorizer.pkl')
        self.model = joblib.load('../lightgbm_model.pkl')
        self.label_encoder = joblib.load('../label_encoder.pkl')

    def predict_disasters_on_list(self, posts):
        print('Adding disaster types to posts')
        for post in posts:
            self.add_disaster_type(post)
        return posts



    def add_disaster_type(self, post):
        input_vector = self.vectorizer.transform([post.text])
        prediction = self.model.predict(input_vector).argmax(axis=1)[0]
        post.disaster_type = self.label_encoder.inverse_transform([prediction])[0]
	
def runscripts():
    predictor = DisasterPredictor()

    print("Starting tweet analysis pipeline")
    data_manager = DataManager()
    fetcher = BlueskyFetcher(data_manager)

    print("Fetching posts from Bluesky")
    posts = fetcher.fetch_posts()
    print(f"Fetched {len(posts)} posts from Bluesky.")

    posts = update_post_locations_on_list(posts)

    posts = predictor.predict_disasters_on_list(posts)

    data_manager.add_bluesky_posts(posts)

    print("Tweet analysis pipeline complete.")

app = Flask(__name__)
	
@app.route('/hello2', methods=['GET'])
def run():
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    runscripts()
    jsonResp = "Complete"
    print(jsonResp)
    return jsonify(jsonResp)

if __name__ == '__main__':
    app.run(host='localhost', port=3000)
	