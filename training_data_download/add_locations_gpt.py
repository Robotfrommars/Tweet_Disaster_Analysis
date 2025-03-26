
from openai import OpenAI
import json
import os
import config

BATCH_SIZE = 1000

def update_post_locations(db):
    print('connecting to ChatGPT...')
    client = OpenAI(api_key=config.open_ai_key)
	
    print('adding post locations...')
    posts = db.get_all_posts()
    
    batches = [posts[i:i + BATCH_SIZE] for i in range(0, len(posts), BATCH_SIZE)]

    for idx, batch in enumerate(batches):
        json_batch = [convert_post(post) for post in batch]
        prompt = f"""For each post in this JSON list, extract the most specific geographic location (city, state, or country) "
            "in the text. Return a new JSON list where each item includes the same 'post_id' and a 'location' string.\n\n"
            "{json.dumps(json_batch, indent=2)}"""

        try:
            response = query_chatgpt(client, prompt)
            updated_posts = json.loads(response)

            for post, updated_data in zip(batch, updated_posts):
                post.location = updated_data.get("location", None)

            print(str(batch))
		    #db.add_bluesky_posts(batch)

        except Exception as e:
            print(f"Connection Error: {e}")
    
def query_chatgpt(client, prompt):
    response = client.chat.completions.create(
        model="o3-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
    
def convert_post(post):
    return {
        "post_id": post.post_id,
        "text": post.text
    }