import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

def train():
    df = pd.read_csv('intents.csv')
    
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    model = MultinomialNB()
    
    X = vectorizer.fit_transform(df['text'])
    y = df['intent']
    
    model.fit(X, y)
    
    model_data = {
        'vectorizer': vectorizer,
        'model': model
    }
    
    joblib.dump(model_data, 'intent_model.pkl')
    print("Model trained successfully! Created 'intent_model.pkl'.")

if __name__ == '__main__':
    train()