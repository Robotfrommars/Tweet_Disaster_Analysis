from atproto import Client

USERNAME = 'ND-Analysis.bsky.social'
PASSWORD = 'Blueskyproject11'

SEARCH_QUERY = "tornado"

def search_bluesky_posts():
    client = Client()
    profile = client.login(USERNAME, PASSWORD)
    print('Logged in as: ', profile.display_name)

    response = client.app.bsky.feed.search_posts({'q': SEARCH_QUERY, 'lang': 'en'})
    
    if not response or not response.posts:
        print("No results found")
        return
        
    print(f'Found {len(response.posts)} posts')
    for post in response.posts:
        print(f'User: {post.author.handle}\nPost: {post.record.text}\n')

search_bluesky_posts()