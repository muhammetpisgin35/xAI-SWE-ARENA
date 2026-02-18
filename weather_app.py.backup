import random
from flask import Flask, request, render_template_string

def get_weather_suggestions(temperature, condition):
    """
    Provide clothing and activity suggestions based on temperature and weather condition.
    - > 20°C: light clothing, sightseeing
    - < 0°C: heavy coat, staying indoors
    - 0-20°C: moderate clothing, versatile activities
    Also factors in condition (e.g., rainy -> umbrella, snowy -> boots).
    """
    # Clothing suggestion based on temp
    if temperature > 20:
        clothing = "light clothing"
        activity = "sightseeing"
    elif temperature < 0:
        clothing = "heavy coat"
        activity = "staying indoors"
    else:
        clothing = "moderate clothing like a jacket"
        activity = "walking or local tours"
    
    # Refine based on weather condition
    condition_lower = condition.lower()
    if "rain" in condition_lower or "storm" in condition_lower:
        clothing += " and umbrella"
    elif "snow" in condition_lower:
        clothing += " and boots"
    elif "wind" in condition_lower:
        clothing += " and windbreaker"
    elif "sunny" in condition_lower or "clear" in condition_lower:
        activity += " or beach time"
    
    return clothing, activity


def generate_weather_data(city):
    """
    Generate random weather data for the given city, including suggestions.
    Reuses core logic from original CLI.
    """
    # List of possible weather conditions
    weather_conditions = [
        "Sunny", "Rainy", "Cloudy", "Windy",
        "Snowy", "Foggy", "Stormy", "Clear",
        "Overcast", "Partly Cloudy"
    ]
    
    # Generate random weather condition and temp
    condition = random.choice(weather_conditions)
    temperature = random.randint(-5, 35)
    
    # Get clothing/activity suggestions
    clothing, activity = get_weather_suggestions(temperature, condition)
    
    return {
        "city": city,
        "condition": condition,
        "temperature": temperature,
        "clothing": clothing,
        "activity": activity
    }


# HTML template for the clean, professional weather page (inline for single-file app)
# Features: form for city input (submit on Enter), styled results display
WEATHER_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather App - Professional Forecast</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f8ff;
            color: #333;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
        }
        form {
            margin-bottom: 20px;
        }
        input[type="text"] {
            padding: 10px;
            width: 70%;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #2980b9;
        }
        .weather-info {
            background: #e8f4f8;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            text-align: left;
        }
        .weather-info p {
            margin: 10px 0;
            font-size: 18px;
        }
        .suggestion {
            font-weight: bold;
            color: #27ae60;
        }
        footer {
            margin-top: 20px;
            font-size: 12px;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Weather Forecast</h1>
        <form method="post" action="/">
            <input type="text" name="city" placeholder="Enter city name (e.g., London)" required autofocus>
            <!-- Submit on Enter keypress; button for accessibility -->
            <button type="submit">Get Weather</button>
        </form>
        {% if weather %}
        <div class="weather-info">
            <p><strong>City:</strong> {{ weather.city }}</p>
            <p><strong>Condition:</strong> {{ weather.condition }}</p>
            <p><strong>Temperature:</strong> {{ weather.temperature }}°C</p>
            <p class="suggestion">Suggestion: Wear {{ weather.clothing }} and consider {{ weather.activity }}.</p>
        </div>
        {% endif %}
        <footer>Powered by random weather generator | Temp range: -5°C to 35°C</footer>
    </div>
</body>
</html>
"""


def main():
    # Keep original CLI for backward compatibility/testing
    # Ask the user for a city name
    city = input("Enter a city name: ").strip()
    
    # Generate weather data
    data = generate_weather_data(city)
    
    # Print the result
    print(f"The weather in {data['city']} is {data['condition']} with a temperature of {data['temperature']}°C.")
    print(f"Suggestions: Wear {data['clothing']} and consider {data['activity']}.")


# Flask web app for the clean weather page
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def weather_page():
    """Render the professional weather page. Handles city input via form (submit on Enter)."""
    weather = None
    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        if city:
            # Generate and display all data for the city
            weather = generate_weather_data(city)
    # Use render_template_string for inline HTML/CSS
    return render_template_string(WEATHER_PAGE_TEMPLATE, weather=weather)

if __name__ == "__main__":
    # Run the web app by default (clean page); CLI via python -m if needed
    # Access at http://127.0.0.1:5001 (changed to avoid port conflicts in testing)
    app.run(debug=True, port=5001)
