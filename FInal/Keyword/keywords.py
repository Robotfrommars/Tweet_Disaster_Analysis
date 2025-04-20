import pandas as pd
from collections import Counter
import re

# Load dataset
file_path = "tweet_data_clean (1).csv"  # Make sure the file is in the same folder
df = pd.read_csv(file_path)

# Column to analyze
TEXT_COLUMN = 'type_of_disaster'

# Keywords to search (case-insensitive)
keywords = ["earthquake", "typhoon", "wildfire", "tornado", "volcano", "pandemic", "meteor", "meteorite", "hurricane","haze", "flood", "cyclone", "collapse", "blizzard", "not disaster"]

# Normalize: lowercase, remove punctuation, and extra spaces
def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)      # Replace multiple spaces with single space
    return text.strip()

# Count keyword occurrences
def count_keywords(df, column, keywords):
    keyword_counter = Counter()
    for text in df[column].dropna():
        norm_text = normalize(text)
        for keyword in keywords:
            # Check for whole words or phrases
            pattern = r'\b' + re.escape(keyword) + r's?\b'  # Match singular or plural
            matches = re.findall(pattern, norm_text)
            keyword_counter[keyword] += len(matches)
    return keyword_counter

# Run it
keyword_counts = count_keywords(df, TEXT_COLUMN, keywords)

# Display the results
print("Keyword Occurrences:")
for kw, count in keyword_counts.items():
    print(f"{kw}: {count}")
