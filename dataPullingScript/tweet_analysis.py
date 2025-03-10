from atproto import Client
from pymongo import MongoClient
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
import os
import re
import emoji


MONGO_URI = "mongodb+srv://armonhadjimani:ND_analysis@cluster0.dqx5o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["disaster_tweets"]
    collection = db["tweets"]
    print("Connected to MongoDB Atlas successfully!")
except Exception as e:
    print(f"MongoDB Connection Error: {e}")
    exit()

USERNAME = "ND-Analysis.bsky.social"
PASSWORD = "Blueskyproject11"
SEARCH_TERMS = ["tornado", "hurricane", "earthquake", "flood", "wildfire", "blizzard", "haze", "meteor"]

def load_cities(filename="worldcities.csv"):
    try:
        df = pd.read_csv(filename, usecols=["city"])
        return set(df["city"].str.lower())
    except Exception as e:
        print(f"Error loading city data: {e}")
        return set()

KNOWN_CITIES = load_cities()

def extract_location(text):
    words = text.lower().split()

    for i in range(len(words)):
        for j in range(i + 1, min(i + 3, len(words) + 1)):
            phrase = " ".join(words[i:j])
            if phrase in KNOWN_CITIES:
                return phrase.title()

    return None

def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = emoji.replace_emoji(text, replace='')
    return text.strip()

def is_duplicate(tweet_data):
    return collection.find_one({"user": tweet_data["user"], "text": tweet_data["text"]}) is not None

def delete_old_posts():
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=5)
    result = collection.delete_many({"timestamp": {"$lt": cutoff_date}})
    print(f"Deleted {result.deleted_count} old tweets from MongoDB.")

def fetch_bluesky_posts(client):
    while True:
        try:
            delete_old_posts()

            all_posts = []
            for term in SEARCH_TERMS:
                response = client.app.bsky.feed.search_posts({'q': term, 'lang': 'en', 'limit': 20})
                if response and response.posts:
                    for post in response.posts:
                        cleaned_text = clean_text(post.record.text)
                        detected_location = extract_location(cleaned_text)

                        tweet_data = {
                            "user": post.author.handle,
                            "text": cleaned_text,
                            "query": term,
                            "timestamp": datetime.fromisoformat(post.record.created_at.replace("Z", "+00:00")) - timedelta(hours=6),
                            "location": detected_location
                        }

                        if not is_duplicate(tweet_data):
                            all_posts.append(tweet_data)

            if all_posts:
                collection.insert_many(all_posts)
                print(f"Inserted {len(all_posts)} new tweets into MongoDB Atlas.")
            else:
                print("No new posts found for the given search terms.")

        except Exception as e:
            print(f"Error fetching Bluesky posts: {e}")

            try:
                print("Re-authenticating with Bluesky...")
                client.login(USERNAME, PASSWORD)
                print("Re-login successful!")
            except Exception as login_error:
                print(f"Re-login failed: {login_error}. Retrying in 5 minutes.")

        print("Waiting for 5 minutes before the next scan")
        time.sleep(300)



try:
    bluesky_client = Client()
    bluesky_client.login(USERNAME, PASSWORD)
    print("Logged in successfully!")

    fetch_bluesky_posts(bluesky_client)

except Exception as e:
    print(f"Bluesky login failed: {e}")
    exit()
