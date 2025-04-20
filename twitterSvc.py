import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC  # Import LinearSVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

#thisd here uses the twitter natural disaster as the data set
data = pd.read_csv('newData.csv')
X = data['tweet_text'] ##Uses teh feature of tweets to figure out the natural disaster
y = data['type_of_disaster']#uses teh label of natural disasters as a feature to classify the naural disaster

vectorizer = TfidfVectorizer(max_features=5000)
X_vectorized = vectorizer.fit_transform(X)

#Here this splita teh dataset into the training and testing set for the model
X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=5)

#this model uses the linear svc algorithm
model = LinearSVC(random_state=5)
model.fit(X_train, y_train) #fitting and traiing the model
y_pred = model.predict(X_test)

#calculates the accuracy of the testing data with the predication the model predicts
accuracy = accuracy_score(y_test, y_pred)

#This section prints acuuracy, classification report, and the confusion matrix fro the model
print(f"Accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
conf_matrix = confusion_matrix(y_test, y_pred)

#This labels the confusin matrix to show the classfication form into a chart
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=model.classes_, yticklabels=model.classes_)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()


