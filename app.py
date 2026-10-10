import os
import json
import re
import joblib
from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types

app = Flask(__name__)

# --- Load Data & ML Model ---
with open("faq.json", "r", encoding="utf-8") as f:
    FAQ_DATA = json.load(f)

# Load trained classifier pipeline safely
classifier = None
if os.path.exists("intent_model.pkl"):
    try:
        classifier = joblib.load("intent_model.pkl")
        print("Successfully loaded intent_model.pkl")
    except Exception as e:
        print(f"Error loading model: {e}")
else:
    print("Warning: intent_model.pkl not found. Run 'python train.py' to generate it.")

# In-memory analytics logging
STATS_LOG = []  # Holds dicts: {"question": str, "category": str, "rating": "up"|"down"|None}

# Common stop words (English & Tagalog/Filipino)
STOP_WORDS = set([
    "the", "is", "at", "which", "on", "a", "an", "and", "or", "to", "in", "for", "of", "what",
    "how", "can", "i", "my", "me", "do", "does", "are", "ang", "ng", "sa", "mga", "na", "pa",
    "ba", "kailan", "ano", "sino", "paano", "may", "meron", "din", "rin", "ako", "ko"
])

def retrieve_top_faqs(user_query, top_n=3):
    """Word-overlap retrieval algorithm for RAG."""
    words = re.findall(r'\w+', user_query.lower())
    filtered_words = set([w for w in words if w not in STOP_WORDS])
    
    if not filtered_words:
        filtered_words = set(words)

    scored_faqs = []
    for faq in FAQ_DATA:
        faq_text = f"{faq['question']} {faq['answer']}".lower()
        faq_words = set(re.findall(r'\w+', faq_text))
        overlap = len(filtered_words.intersection(faq_words))
        scored_faqs.append((overlap, faq))

    scored_faqs.sort(key=lambda x: x[0], reverse=True)
    return [faq for _, faq in scored_faqs[:top_n]]

@app.route("/")
def index_page():
    return render_template("index.html")

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        message = data.get("message", "").strip()

        # Validation checks
        if not message:
            return jsonify({"error": "Message cannot be empty."}), 400
        if len(message) > 500:
            return jsonify({"error": "Message exceeds max length of 500 characters."}), 400

        # ML Category Prediction
        predicted_category = "general"
        if classifier:
            try:
                predicted_category = classifier.predict([message])[0]
            except Exception as e:
                print(f"Classification error: {e}")

        # Retrieve Top 3 FAQs
        retrieved_faqs = retrieve_top_faqs(message, top_n=3)
        retrieved_ids = [faq["id"] for faq in retrieved_faqs]

        # Construct Gemini Prompt
        context_str = json.dumps(retrieved_faqs, indent=2)
        prompt = f"""You are Bayanihan College's Enrollment Helpdesk Assistant.
Answer the student's question based ONLY on the following official FAQ entries:

{context_str}

RULES:
1. Answer strictly using ONLY the provided FAQ entries. Do not assume or extrapolate policies.
2. If the answer is NOT explicitly found in the provided FAQ entries, reply with: "I am sorry, but I do not have official information regarding that query. Please contact the Registrar's Office directly for further assistance."
3. Respond in the same language as the user's question (English, Tagalog, or Taglish).
4. Maintain a polite, clear, and helpful tone.

User Question: {message}"""

        # Call Gemini API
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            answer_text = "System configuration error: GEMINI_API_KEY environment variable is missing."
        else:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.1)
                )
                answer_text = response.text.strip()
            except Exception as err:
                print(f"Gemini API Exception: {err}")
                answer_text = "I'm having trouble connecting to my service right now. Please try again later."

        # Log analytics entry
        log_entry = {
            "question": message,
            "category": predicted_category,
            "rating": None
        }
        STATS_LOG.append(log_entry)

        return jsonify({
            "answer": answer_text,
            "faq_ids": retrieved_ids,
            "category": predicted_category,
            "log_index": len(STATS_LOG) - 1
        })

    except Exception as server_err:
        print(f"Unhandled Server Error: {server_err}")
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route("/api/rate", methods=["POST"])
def rate_response():
    data = request.get_json() or {}
    log_index = data.get("log_index")
    rating = data.get("rating")

    if log_index is not None and 0 <= log_index < len(STATS_LOG):
        STATS_LOG[log_index]["rating"] = rating
        return jsonify({"status": "success"})
    return jsonify({"error": "Invalid log index"}), 400

@app.route("/api/stats", methods=["GET"])
def stats():
    category_counts = {}
    thumbs_up = 0
    total_rated = 0

    for item in STATS_LOG:
        cat = item["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

        if item["rating"] == "up":
            thumbs_up += 1
            total_rated += 1
        elif item["rating"] == "down":
            total_rated += 1

    percentage_up = (thumbs_up / total_rated * 100) if total_rated > 0 else 0.0

    return jsonify({
        "questions_per_category": category_counts,
        "total_questions": len(STATS_LOG),
        "total_rated": total_rated,
        "thumbs_up_percentage": round(percentage_up, 1)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)