from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
api_key = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city_name):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "imperial"  # Fahrenheit because this is America
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return {
            "city": city_name,
            "temperature_F": data['main']['temp'],
            "weather_description": data['weather'][0]['description'],
            "humidity_percent": data['main']['humidity']
        }
    else:
        print(f"Failed to retrieve data for {city_name} — {response.status_code}")
        return None

# 📝 Collect data
cities = ["Los Angeles", "San Francisco", "Seattle"]
weather_data = []

for city in cities:
    result = get_weather(city)
    if result:
        weather_data.append(result)

# 💾 Save to JSON
with open("weather_data.json", "w") as f:
    json.dump(weather_data, f, indent=4)

print("\n✅ Data written to weather_data.json") 