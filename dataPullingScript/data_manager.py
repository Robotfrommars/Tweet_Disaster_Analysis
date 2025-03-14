from pymongo import MongoClient, ReplaceOne
from typing import List
from datetime import datetime, timedelta, timezone
import config


class DataManager:
    def __init__(self):
        print("Connecting to MongoDB Atlas...")
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

    def get_all_posts(self):
        return list(self.collection.find())  # Returns raw MongoDB documents

    def add_bluesky_posts(self, posts: List[dict]):
        if not posts:
            return

        operations = [
            ReplaceOne({"user": post["user"], "text": post["text"]}, post, upsert=True)
            for post in posts
        ]
        result = self.collection.bulk_write(operations)
        print(f"Inserted/Updated {result.upserted_count} posts.")

    def is_duplicate(self, post: dict) -> bool:
        return self.collection.find_one({"user": post["user"], "text": post["text"]}) is not None

    def delete_old_posts(self):
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=5)
        result = self.collection.delete_many({"createdAt": {"$lt": cutoff_date}})
        print(f"Deleted {result.deleted_count} old posts from MongoDB.")
