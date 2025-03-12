from atproto import Client
from data_manager import DataManager
from models import BlueskyPost

import add_locations as locations

USERNAME = 'ND-Analysis.bsky.social'
PASSWORD = 'Blueskyproject11'

#we can modify search parameter to other disasters
SEARCH_QUERIES = ['Earthquake', 'Tornado', 'Wildfire', 'Hurricane', 'Flood', 'Blizzard']

# modify search date range to find posts in a certain period
START_DATE = '2025-01-01T00:00:00Z'
END_DATE = '2025-02-25T00:00:00Z'

MAX_DOWNLOADS = 250

print('Logging in to bluesky API...')

client = Client()
profile = client.login(USERNAME, PASSWORD)

data_manager = DataManager()

#locations.update_post_locations(data_manager)

def search_bluesky_posts(cursor, q):
	# search parameter: https://docs.bsky.app/docs/api/app-bsky-feed-search-posts
    response = client.app.bsky.feed.search_posts({
		'q': q, 
		'lang': 'en', 
		'since': START_DATE, 
		'until': END_DATE, 
		'limit' : 100,
		'cursor': cursor
	})
    
    if not response or not response.posts:
        print("No results found")
        return
        
    print(f'Found {len(response.posts)} posts')
    results = []
	
    for post in response.posts:
        results.append(BlueskyPost(
            post_id = str(post.uri),
            createdAt = post.record.created_at,
            text = post.record.text,
            disaster_type='NONE'
        ))
		
    next_cursor = response.cursor if hasattr(response, 'cursor') else None
    return results, next_cursor

for q in SEARCH_QUERIES:
	downloaded_count = 0
	cursor = None
	
	while downloaded_count < MAX_DOWNLOADS:
		print(f'Searching posts for {q} at index {downloaded_count}')
		posts, cursor = search_bluesky_posts(cursor, q)
		if not posts:
			break

		data_manager.add_bluesky_posts(posts)
		downloaded_count += 1
		
		if downloaded_count >= MAX_DOWNLOADS or not cursor:
			break
