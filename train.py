import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def train_intent_model():
    print("Loading intents dataset...")
    df = pd.read_csv("intents.csv")
    
    X = df["question"]
    y = df["category"]

    # 80/20 train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Machine learning pipeline: TF-IDF + Naive Bayes Classifier
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), stop_words=None),
        MultinomialNB(alpha=0.5)
    )

    print("Training model...")
    model.fit(X_train, y_train)

    # Evaluate model performance
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n" + "="*40)
    print(f"MODEL ACCURACY: {accuracy * 100:.2f}%")
    print("="*40)
    print("\nCLASSIFICATION REPORT:")
    print(classification_report(y_test, y_pred))
    
    print("\nCONFUSION MATRIX:")
    labels = sorted(y.unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    print(cm_df)

    # Save model pipeline
    joblib.dump(model, "intent_model.pkl")
    print("\nModel saved successfully as 'intent_model.pkl'")

if __name__ == "__main__":
    train_intent_model()