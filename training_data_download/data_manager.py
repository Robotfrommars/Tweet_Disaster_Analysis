

import pymongo
from pymongo import MongoClient, ReplaceOne
from typing import List, Dict
import ssl
from models import BlueskyPost  
import config  

class DataManager:
    def __init__(self):
        print('Connecting to database...')
        client = MongoClient(config.mongo_url, config.mongo_port, tls=True, tlsAllowInvalidCertificates=True)
        self.db = client[config.db_name]
        self.bluesky_posts = self.db['cs-project-db.bluesky-posts']
        print('Connection successful!')
        
    def get_all_posts(self):
        return [BlueskyPost(**document) for document in self.bluesky_posts.find()]

    def add_bluesky_post(self, post: BlueskyPost):
        self.bluesky_posts.replace_one({"post_id": post.post_id}, post.dict(), upsert=True)

    def add_bluesky_posts(self, posts: List[BlueskyPost]):
        operations = [
            ReplaceOne({"post_id": post.post_id}, post.dict(), upsert=True)
            for post in posts
        ]
        if operations:
            self.bluesky_posts.bulk_write(operations)
