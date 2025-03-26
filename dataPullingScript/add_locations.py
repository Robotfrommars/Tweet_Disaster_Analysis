import spacy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
import time

nlp = spacy.load("en_core_web_sm")

geolocator = Nominatim(user_agent="tweet-disaster-locator")
location_cache = {}


def update_post_locations(db):
    posts = db.get_all_posts()
    print('Adding post locations and coordinates')

    for post in posts:
        add_location(post)
    db.add_bluesky_posts(posts)

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
        time.sleep(1)
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
