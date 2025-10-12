# app.py
from flask import Flask, request, jsonify
import pandas as pd
import os
import random
import requests
from wardrobe_utils import load_wardrobe_from_json, determine_season

app = Flask(__name__)

# Replace with your own OpenWeatherMap API key
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"

def get_current_weather(city):
    """
    Fetch current weather from OpenWeatherMap API.
    Returns 'hot', 'moderate', 'rainy', or 'winter'.
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        r = requests.get(url)
        data = r.json()
        weather = data['weather'][0]['main'].lower()
        if "rain" in weather:
            return "rainy"
        elif "clear" in weather:
            return "hot"
        elif "cloud" in weather:
            return "moderate"
        else:
            return "winter"
    except Exception:
        return "moderate"  # Default if API fails

@app.route('/')
def home():
    return jsonify({"message": "👗 Wardrobe API is running!"})

@app.route('/suggest_outfit', methods=['POST'])
def suggest_outfit():
    """
    Receives JSON from Flutter:
    {
      "city": "Bangalore",
      "event": "casual",
      "wardrobe": [ {clothing items from Hive} ]
    }
    Returns a suggested outfit (top + bottom) in JSON.
    """
    data = request.get_json()

    # Validate request
    if not data or 'wardrobe' not in data or 'city' not in data:
        return jsonify({"error": "Missing 'wardrobe' or 'city' in request"}), 400

    df = load_wardrobe_from_json(data['wardrobe'])
    if df.empty:
        return jsonify({"error": "Wardrobe is empty. Please upload items first."}), 400

    city = data['city']
    event = data.get('event', 'casual')

    # Detect current weather
    weather = get_current_weather(city)

    # Filter wardrobe by season + category
    tops = df[(df['category'].str.lower() == 'top') & (df['season'].str.lower() == weather)]
    bottoms = df[(df['category'].str.lower() == 'bottom') & (df['season'].str.lower() == weather)]

    if tops.empty or bottoms.empty:
        return jsonify({"message": "No suitable outfit found for this weather."})

    # Randomly pick one top and one bottom
    top_item = tops.sample(1).iloc[0].to_dict()
    bottom_item = bottoms.sample(1).iloc[0].to_dict()

    return jsonify({
        "weather": weather,
        "event": event,
        "top": top_item,
        "bottom": bottom_item,
        "message": f"Outfit suggested for {event} in {city}"
    })

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render port, fallback 10000
    app.run(host="0.0.0.0", port=port)

