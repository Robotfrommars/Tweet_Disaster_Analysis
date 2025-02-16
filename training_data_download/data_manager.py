

import pymongo
from pymongo import MongoClient
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
        self.bluesky_posts.insert_one(post.dict())
