import pandas as pd

a = pd.read_csv("processed_sampled_tweets.csv")
print(a.head())
print(a.info())
print(a.describe())
a.to_csv("modified_file.csv", index=False)

