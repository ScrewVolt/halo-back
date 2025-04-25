from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

@app.route("/summary", methods=["POST"])
def generate_summary():
    data = request.json
    messages = data.get("messages", "")
    print("🔍 Incoming messages:", messages)

    prompt = f"""You're a medical AI trained to generate DAR format nursing notes.
Given this conversation between a nurse and patient, generate a detailed DAR note:

{messages}

Respond only with the formatted DAR note in markdown.
"""

    try:
        print("🧠 Sending to OpenAI...")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                { "role": "system", "content": "You are a medical AI assistant that generates structured nursing summaries." },
                { "role": "user", "content": prompt }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        dar = response.choices[0].message.content
        print("✅ Received response.")
        return jsonify({ "dar": dar })

    except Exception as e:
        print("❌ OpenAI API error:", str(e))  # 💥 This will show us the exact issue
        return jsonify({ "error": str(e) }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
