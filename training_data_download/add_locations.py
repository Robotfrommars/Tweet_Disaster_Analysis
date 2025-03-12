
import spacy

nlp = spacy.load("en_core_web_sm")

def update_post_locations(db):
    posts = db.get_all_posts()
    print('adding post locations...')
    
    for post in posts:
        add_location(post)
    db.add_bluesky_posts(posts)
	
def add_location(post):
    try:
        if post.text is not None and len(post.text) > 0 and len(post.location) == 0:
            location = extract_locations(post.text)
            post.location = location
            print(f'Added location {location} to tweet data')
    except Exception as e:
        print(f'Error adding location data: {e}')
    return None
	
def extract_locations(text):
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    return list(set(locations))
    