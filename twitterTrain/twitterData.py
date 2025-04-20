import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import joblib

#this here uses the twitter natural disaster as the data set
data = pd.read_csv('newData.csv')
X = data['tweet_text'] #Uses the feature of tweets to figure out the natural disaster
y = data['type_of_disaster'] #Uses the label of natural disasters as a feature to classify the natural disaster
vectorizer = TfidfVectorizer(max_features=5000)
X_vectorized = vectorizer.fit_transform(X)

#Here this splits the dataset into the training and testing set for the model
X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=5)

#this model uses the logistic regression algorithm for classifying the dataset
model = LogisticRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

#This section prints accuracy of the model as well as display the classification report for the labels as well
accuracy = accuracy_score(y_test, y_pred)#calculates the accuracy of the testing data with the predication the model predicts
print(f"Accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

#This labels and print out the confusion matrix to show the classification report in a chart format
conf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=model.classes_, yticklabels=model.classes_)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()

