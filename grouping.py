import pandas as pd
from collections import Counter
import re

# Load the dataset
file_path = "tweet_data_clean (1).csv"  # Make sure the file is in the same directory or adjust the path
df = pd.read_csv(file_path)

# Column to analyze
TEXT_COLUMN = 'tweet_text'

# Keywords to search for (case-insensitive)
keywords = ["earthquake", "typhoon", "wildfire", "tsunami", "not disaster"]

# Tokenization function
def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

# Count keyword occurrences
def count_keywords(df, column, keywords):
    keyword_counter = Counter()
    for text in df[column].dropna():
        text_lower = text.lower()
        for keyword in keywords:
            if ' ' in keyword:
                keyword_counter[keyword] += text_lower.count(keyword)
            else:
                tokens = tokenize(text_lower)
                keyword_counter[keyword] += tokens.count(keyword)
    return keyword_counter

# Get keyword counts
keyword_counts = count_keywords(df, TEXT_COLUMN, keywords)

# Display the results
print("Keyword Occurrences:")
for kw, count in keyword_counts.items():
    print(f"{kw}: {count}")
import pandas as pd
from collections import Counter
import re

# Load the dataset
file_path = "tweet_data_clean (1).csv"  # Make sure the file is in the same directory or adjust the path
df = pd.read_csv(file_path)

# Column to analyze
TEXT_COLUMN = 'tweet_text'

# Keywords to search for (case-insensitive)
keywords = ["earthquake", "typhoon", "wildfire", "tsunami", "not disaster"]

# Tokenization function
def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

# Count keyword occurrences
def count_keywords(df, column, keywords):
    keyword_counter = Counter()
    for text in df[column].dropna():
        text_lower = text.lower()
        for keyword in keywords:
            if ' ' in keyword:
                keyword_counter[keyword] += text_lower.count(keyword)
            else:
                tokens = tokenize(text_lower)
                keyword_counter[keyword] += tokens.count(keyword)
    return keyword_counter

# Get keyword counts
keyword_counts = count_keywords(df, TEXT_COLUMN, keywords)

# Display the results
print("Keyword Occurrences:")
for kw, count in keyword_counts.items():
    print(f"{kw}: {count}")
