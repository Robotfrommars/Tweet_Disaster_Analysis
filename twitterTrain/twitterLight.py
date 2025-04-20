import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import lightgbm as lgb
import joblib
from sklearn.preprocessing import LabelEncoder

#this set reads the dataset and splits the model into the training and testing set
data = pd.read_csv('newData.csv')
X = data['tweet_text'] #uses the features from the tweet to help indetify the diaster from thr tweets
y = data['type_of_disaster'] #uses teh feature of the natural disasters to label the tweet
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
vectorizer = TfidfVectorizer(
    max_features=3000,
    ngram_range=(1, 2),
    min_df=5,
    max_df=0.8
)

X_vectorized = vectorizer.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized, y_encoded,
    test_size=0.2,
    random_state=5,
    stratify=y_encoded
)

#This creates the testing data and splits the datat nto 80% train 20% test
train_data = lgb.Dataset(X_train, label=y_train)
test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

#These paramaters are used to creating  the model an how they are traing it
params = {
    'objective': 'multiclass',
    'num_class': len(label_encoder.classes_),
    'metric': 'multi_logloss',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.7,
    'bagging_fraction': 0.7,
    'bagging_freq': 5,
    'min_child_samples': 20,
    'reg_alpha': 0.1,
    'reg_lambda': 0.1,
    'verbose': -1,
    'random_state': 5
}

#This creates the the model using the light gbm model
model = lgb.train(
    params,
    train_data,
    valid_sets=[test_data],
    num_boost_round=500,
    callbacks=[lgb.early_stopping(stopping_rounds=10), lgb.log_evaluation(-1)]
)

#This section is what creates the model and sets it up displaying thre cacurate rate and deploying the report on how the results averaged.
y_pred = model.predict(X_test)
y_pred_classes = y_pred.argmax(axis=1)
y_pred_labels = label_encoder.inverse_transform(y_pred_classes)
y_test_labels = label_encoder.inverse_transform(y_test)

#print out the accuracy of the model as well as the classification report for it
accuracy = accuracy_score(y_test_labels, y_pred_labels)
print(f"Accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test_labels, y_pred_labels))

#creates the confusion matrix for the model
conf_matrix = confusion_matrix(y_test_labels, y_pred_labels)
plt.figure(figsize=(10, 8))
(sns.heatmap
(
    conf_matrix,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=label_encoder.classes_,
    yticklabels=label_encoder.classes_
))

#labels the moddel and shows which sid is predicted and curracy to property display the report.
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()
joblib.dump(model, 'lightgbm_model.pkl')
joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
joblib.dump(label_encoder, 'label_encoder.pkl')