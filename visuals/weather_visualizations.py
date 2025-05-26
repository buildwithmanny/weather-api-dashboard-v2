import matplotlib.pyplot as plt
import json

# Load the saved data
with open("weather_data.json", "r") as f:
    data = json.load(f)

# Extract cities and temperatures
cities = [entry["city"] for entry in data]
temperatures = [entry["temperature_F"] for entry in data]

# Create a bar chart
plt.figure(figsize=(8, 5))
plt.bar(cities, temperatures, color="skyblue")
plt.title("Temperature Comparison (°F)")
plt.xlabel("City")
plt.ylabel("Temperature (°F)")
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Show the plot
plt.tight_layout()
plt.show() 