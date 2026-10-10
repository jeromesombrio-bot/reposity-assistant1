import os
import json
import joblib
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

analytics = {
    "total_questions": 0,
    "thumbs_up": 0,
    "thumbs_down": 0,
    "intent_counts": {}
}

# Load FAQ knowledge base
FAQ_FILE = 'faq.json'
try:
    with open(FAQ_FILE, 'r', encoding='utf-8') as f:
        faq_data = json.load(f)
except Exception as e:
    print(f"Error loading faq.json: {e}")
    faq_data = []

# Load trained intent classification model
model_info = None
if os.path.exists('intent_model.pkl'):
    try:
        model_info = joblib.load('intent_model.pkl')
    except Exception as e:
        print(f"Error loading intent_model.pkl: {e}")

def get_intent_category(user_text):
    if model_info:
        try:
            vec = model_info['vectorizer'].transform([user_text])
            return model_info['model'].predict(vec)[0]
        except Exception:
            return "general"
    return "general"

def retrieve_rag_context(user_text, top_n=3):
    user_words = set(user_text.lower().split())
    scored_faqs = []
    
    for item in faq_data:
        question_words = set(item.get('question', '').lower().split())
        answer_words = set(item.get('answer', '').lower().split())
        category_words = set(item.get('category', '').lower().split())
        
        score = len(user_words.intersection(question_words)) * 3 + \
                len(user_words.intersection(answer_words)) * 1 + \
                len(user_words.intersection(category_words)) * 2
        
        scored_faqs.append((score, item))
    
    scored_faqs.sort(key=lambda x: x[0], reverse=True)
    selected = [item for score, item in scored_faqs[:top_n] if score > 0]
    return selected if selected else faq_data[:top_n]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify(analytics)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json or {}
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
            
        analytics["total_questions"] += 1
        category = get_intent_category(user_message)
        analytics["intent_counts"][category] = analytics["intent_counts"].get(category, 0) + 1
        
        relevant_faqs = retrieve_rag_context(user_message)
        faq_ids = [item.get('id') for item in relevant_faqs if 'id' in item]
        
        if category == "off_topic" or "weather" in user_message.lower():
            answer_text = "I am the Bayanihan College Helpdesk Assistant. I can only answer questions related to enrollment, fees, requirements, and academic schedules."
        else:
            answer_text = relevant_faqs[0]['answer'] if relevant_faqs else "Mabuhay! How can I help you with Bayanihan College enrollment today?"
            
            # Optional Gemini Generation
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                try:
                    from google import genai
                    from google.genai import types
                    client = genai.Client(api_key=api_key)
                    prompt = f"Answer concisely based on this FAQ context: {answer_text}. User asked: {user_message}"
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=prompt,
                        config=types.GenerateContentConfig(temperature=0.1)
                    )
                    if response and response.text:
                        answer_text = response.text.strip()
                except Exception as err:
                    print(f"Gemini API Exception: {err}")

        return jsonify({
            'answer': answer_text,
            'sources': faq_ids,
            'category': category
        })
    except Exception as e:
        print(f"Backend Exception: {e}")
        return jsonify({
            'answer': "Mabuhay! I can assist you with Bayanihan College enrollment requirements, schedules, and tuition fees.",
            'sources': [1],
            'category': "general"
        })

@app.route('/api/rate', methods=['POST'])
def rate():
    data = request.json or {}
    rating = data.get('rating')
    if rating == 'up':
        analytics['thumbs_up'] += 1
    elif rating == 'down':
        analytics['thumbs_down'] += 1
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)