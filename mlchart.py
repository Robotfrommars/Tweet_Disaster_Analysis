import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import seaborn as sns
import matplotlib.pyplot as plt

# ---------------------------------------------
# Load the dataset
# ---------------------------------------------
df = pd.read_csv('sampled_tweets.csv')

# Print the column names to check for the correct column
print("Column Names:", df.columns)

# Preview the first few rows of the dataset
print("First few rows of the dataset:\n", df.head())

# ---------------------------------------------
# Define disaster-related keywords
# ---------------------------------------------
disaster_keywords = {
    'hurricane': ['hurricane', 'cyclone'],
    'blizzard': ['blizzard', 'snowstorm', 'snow storm'],
    'flood': ['flood', 'flash flood', 'overflow', 'inundation'],
    'tornado': ['tornado', 'twister', 'whirlwind'],
    'wildfire': ['wildfire', 'forest fire', 'bushfire'],
    'typhoon': ['typhoon'],
    'meteorite': ['meteorite', 'meteor', 'asteroid'],
}

# ---------------------------------------------
# Function to count disaster-related keywords in a tweet
# ---------------------------------------------
def count_keywords(tweet, disaster_keywords):
    tweet = tweet.lower()  # Convert tweet to lowercase
    keyword_counts = {}

    for disaster, keywords in disaster_keywords.items():
        count = sum(tweet.count(keyword) for keyword in keywords)
        keyword_counts[disaster] = count

    # Count 'not disaster' as 1 if no disaster keywords matched
    if all(count == 0 for count in keyword_counts.values()):
        keyword_counts['not_disaster'] = 1
    else:
        keyword_counts['not_disaster'] = 0

    return keyword_counts

# ---------------------------------------------
# Apply keyword counting function to each tweet
# ---------------------------------------------
keyword_counts = df['tweet_text'].apply(lambda x: count_keywords(x, disaster_keywords))

# Convert the list of counts into a DataFrame
keyword_df = pd.DataFrame(keyword_counts.tolist())

# Concatenate the keyword counts with the original dataset
df_with_keywords = pd.concat([df, keyword_df], axis=1)

# Display the keyword counts alongside the tweet text
print("\nKeyword Counts for Each Tweet:\n")
print(df_with_keywords[['tweet_text'] + list(disaster_keywords.keys()) + ['not_disaster']].head(20))

# ---------------------------------------------
# Count total occurrences of each disaster type in the dataset
# ---------------------------------------------
total_counts = {}

for column in disaster_keywords.keys():
    total_counts[column] = df_with_keywords[column].astype(int).sum()

# Count how many tweets are "not disaster"
total_counts['not_disaster'] = df_with_keywords['not_disaster'].astype(int).sum()

# Print total occurrences of each disaster type
print("\nTotal Occurrences of Each Disaster Type (across all tweets):")
for disaster, count in total_counts.items():
    print(f"{disaster.capitalize()}: {count}")

# ---------------------------------------------
# Prepare data for model training (example: target 'hurricane')
# ---------------------------------------------

# Select features (X) and target (y)
X = df_with_keywords.drop(columns=['tweet_text', 'hurricane'])  # Use hurricane as example target
X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

# Create the target variable (1 if hurricane is present, else 0)
y = df_with_keywords['hurricane']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the RandomForest model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Make predictions and evaluate the model
y_pred = model.predict(X_test)

# Print the classification report with zero_division=1 to suppress warnings
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred, zero_division=1))

# ---------------------------------------------
# Bar Plot: Total Occurrences of Each Disaster Type
# ---------------------------------------------

# Convert total_counts dictionary to a DataFrame
counts_df = pd.DataFrame(list(total_counts.items()), columns=['Disaster Type', 'Count'])

# Optional: Sort by count, descending
counts_df = counts_df.sort_values(by='Count', ascending=False)

# Create the bar plot with explicit hue assignment (future-proof fix)
plt.figure(figsize=(10, 6))
sns.barplot(
    x='Disaster Type',
    y='Count',
    hue='Disaster Type',        # Assign hue to prevent future warnings
    data=counts_df,
    palette='viridis',
    legend=False                # Hide redundant legend
)

# Customize plot labels and title
plt.title('Total Occurrences of Each Disaster Type in the Dataset', fontsize=14)
plt.xlabel('Disaster Type', fontsize=12)
plt.ylabel('Count', fontsize=12)

# Rotate x-axis labels for readability
plt.xticks(rotation=45)

# Show the plot
plt.tight_layout()
plt.show()
