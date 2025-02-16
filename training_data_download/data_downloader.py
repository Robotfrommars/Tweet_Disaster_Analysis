from atproto import Client
from data_manager import DataManager
from models import BlueskyPost

USERNAME = 'ND-Analysis.bsky.social'
PASSWORD = 'Blueskyproject11'

#we can modify search parameter to other disasters
SEARCH_QUERY = "hurricane"

# modify search date range to find posts in a certain period
START_DATE = '2025-01-01T00:00:00Z'
END_DATE = '2025-01-10T00:00:00Z'

def search_bluesky_posts():
    client = Client()
    profile = client.login(USERNAME, PASSWORD)
    print('Logged in as: ', profile.display_name)

	# search parameter: https://docs.bsky.app/docs/api/app-bsky-feed-search-posts
    response = client.app.bsky.feed.search_posts({'q': SEARCH_QUERY, 'lang': 'en', 'since': START_DATE, 'until': END_DATE, 'limit' : 100})
    
    if not response or not response.posts:
        print("No results found")
        return
        
    print(f'Found {len(response.posts)} posts')
    results = []
	
    for post in response.posts:
        results.append(BlueskyPost(
            _id = str(post.uri),
            createdAt = post.record.created_at,
            text = post.record.text,
            disaster_type='NONE'
        ))
    return results

data_manager = DataManager()
posts = search_bluesky_posts()

for post in posts:
	data_manager.add_bluesky_post(post)
