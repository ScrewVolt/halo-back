from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Instantiate the new client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app)

@app.route("/summary", methods=["POST"])
def generate_summary():
    data = request.json or {}
    messages = data.get("messages", "")
    format_type = data.get("format", "DAR").upper()
    print(f"🔍 Incoming format: {format_type}")
    print("🔍 Incoming messages:", messages)

    # Format instructions
    format_prompts = {
        "DAR": "Generate a detailed DAR (Data, Action, Response) nursing note in markdown format.",
        "SOAP": "Generate a detailed SOAP (Subjective, Objective, Assessment, Plan) nursing note in markdown format.",
        "BIRP": "Generate a detailed BIRP (Behavior, Intervention, Response, Plan) nursing note in markdown format."
    }
    if format_type not in format_prompts:
        return jsonify({ "error": f"Unsupported format: {format_type}" }), 400

    # Build system+user messages
    chat_messages = [
        { "role": "system", "content": "You are a medical AI assistant that generates structured nursing summaries." },
        { "role": "user",   "content": (
            f"You are a medical AI assistant trained in nursing documentation.\n"
            f"{format_prompts[format_type]}\n\n"
            f"Conversation between nurse and patient:\n{messages}\n\n"
            f"Respond only with the formatted {format_type} note in markdown."
        )}
    ]

    try:
        print("🧠 Sending to OpenAI (v1.0+ client)...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=chat_messages,
            temperature=0.3,
            max_tokens=1000
        )
        note = response.choices[0].message.content
        print("✅ Received response.")
        return jsonify({ "note": note, "format": format_type })

    except Exception as e:
        print("❌ OpenAI API error:", str(e))
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
