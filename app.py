# -*- coding: utf-8 -*-
"""
Outfit Suggestion API using Google Gemini 2.5
"""

from flask import Flask, request, jsonify
import google.generativeai as genai
import os

# Initialize Flask app
app = Flask(__name__)

# Configure Google Gemini API
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ Missing GOOGLE_API_KEY environment variable.")
genai.configure(api_key=api_key)

# Load Gemini model
model = genai.GenerativeModel("models/gemini-2.5-flash")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Outfit Suggestion API 👕"})


@app.route("/suggest_outfit", methods=["POST"])
def suggest_outfit():
    try:
        data = request.get_json()

        # Extract user details safely
        gender = data.get("gender", "unisex")
        location = data.get("location", "Unknown")
        event = data.get("event", "casual")
        size = data.get("size", "M")
        weather = data.get("weather", "normal")

        # Build Gemini prompt
        prompt = f"""
        You are a fashion assistant.
        Suggest a short and friendly outfit idea for:
        - Gender: {gender}
        - Location: {location}
        - Event: {event}
        - Size: {size}
        - Weather: {weather}

        Output: A short, natural outfit suggestion in one sentence.
        """

        # Generate suggestion from Gemini
        response = model.generate_content(prompt)
        suggestion = response.text.strip()

        return jsonify({
            "success": True,
            "suggestion": suggestion
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
