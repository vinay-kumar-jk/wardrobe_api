# app.py
from flask import Flask, request, jsonify
import pandas as pd
import os
import random
import requests
from wardrobe_utils import load_wardrobe_from_json, determine_season

app = Flask(__name__)

# Load the API key from environment variables for security
API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")

def get_current_weather(city):
    """
    Fetch current weather from OpenWeatherMap API.
    Returns 'hot', 'moderate', 'rainy', or 'winter' based on weather and temperature.
    """
    if not API_KEY:
        print("Warning: OPENWEATHERMAP_API_KEY is not set. Returning 'moderate' as default.")
        return "moderate"

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        r = requests.get(url)
        r.raise_for_status()  # This will raise an error for bad responses (4xx or 5xx)
        data = r.json()
        
        weather_main = data['weather'][0]['main'].lower()
        temp = data['main']['temp'] # Temperature in Celsius

        # Determine season based on weather type and temperature
        if "rain" in weather_main or "drizzle" in weather_main or "thunderstorm" in weather_main:
            return "rainy"
        elif temp > 28:
            return "hot"
        elif temp < 15:
            return "winter"
        else:  # Covers moderate temperatures between 15°C and 28°C
            return "moderate"
            
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to weather API: {e}")
        return "moderate"  # Default if API fails

@app.route('/')
def home():
    return jsonify({"message": "👗 Wardrobe API is running!"})

@app.route('/suggest_outfit', methods=['POST'])
def suggest_outfit():
    """
    Receives JSON from Flutter, determines the season for each item,
    and suggests an outfit based on current weather.
    """
    data = request.get_json()

    if not data or 'wardrobe' not in data or 'city' not in data:
        return jsonify({"error": "Missing 'wardrobe' or 'city' in request"}), 400

    df = load_wardrobe_from_json(data['wardrobe'])
    if df.empty:
        return jsonify({"error": "Wardrobe is empty. Please add items first."}), 400
        
    # --- FIX: Determine the season for each item dynamically ---
    # Your Flutter app must send 'material' and 'coverage' for each item.
    if 'material' not in df.columns or 'coverage' not in df.columns:
        return jsonify({"error": "Each wardrobe item must have 'material' and 'coverage' keys."}), 400
    df['season'] = df.apply(lambda row: determine_season(row['material'], row['coverage']), axis=1)

    city = data['city']
    event = data.get('event', 'casual')
    weather = get_current_weather(city)

    # Filter wardrobe by the calculated season that matches the current weather
    tops = df[(df['category'].str.lower() == 'top') & (df['season'] == weather)]
    bottoms = df[(df['category'].str.lower() == 'bottom') & (df['season'] == weather)]

    if tops.empty or bottoms.empty:
        return jsonify({
            "weather": weather,
            "message": f"Sorry, no matching {'tops' if tops.empty else 'bottoms'} were found for the current weather ({weather})."
        })

    # Randomly pick one top and one bottom from the filtered list
    top_item = tops.sample(1).iloc[0].to_dict()
    bottom_item = bottoms.sample(1).iloc[0].to_dict()

    return jsonify({
        "weather": weather,
        "event": event,
        "top": top_item,
        "bottom": bottom_item,
        "message": f"Here is your outfit for a {event} day in {city}!"
    })

if __name__ == "__main__":
    # Use the PORT environment variable provided by Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)