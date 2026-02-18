import random
import json
import os
import re  # For city name validation (letters/spaces only)
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


# JSON persistence for favorites and search history (as requested)
JSON_FILE = "favorites.json"
DEFAULT_DATA = {"favorites": [], "search_history": []}


def load_data():
    """Load favorites and search_history from JSON file on startup. Create defaults if not exists."""
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r") as f:
                data = json.load(f)
                # Ensure structure and limit history to last 5
                data.setdefault("favorites", [])
                data.setdefault("search_history", [])
                data["search_history"] = data["search_history"][:5]
                return data
        except (json.JSONDecodeError, IOError):
            pass  # Fall back to defaults on error
    return DEFAULT_DATA.copy()


def save_data(data):
    """Save updated data to JSON file immediately on changes."""
    try:
        with open(JSON_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving data: {e}")


def add_to_history(data, city):
    """Add city to search history (last 5 unique, most recent first)."""
    if city and city not in data["search_history"]:
        data["search_history"].insert(0, city)
        data["search_history"] = data["search_history"][:5]
    return data


def add_to_favorites(data, city):
    """Add city to favorites if not already present."""
    if city and city not in data["favorites"]:
        data["favorites"].append(city)
    return data


# HTML template for the clean, professional weather page (inline for single-file app)
# Features: form for city input (submit on Enter), styled results display.
# Enhanced with validation: only letters/spaces allowed for city names; warning for invalid (no weather data shown).
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
        input.invalid {
            border-color: #e74c3c;  /* Red border for invalid */
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
        .error {
            color: #e74c3c;  /* Red for warnings */
            background: #fdf2f2;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-weight: bold;
        }
        footer {
            margin-top: 20px;
            font-size: 12px;
            color: #777;
        }
        /* JS for real-time feedback */
        .input-hint {
            font-size: 12px;
            color: #777;
            margin-top: 5px;
        }
    </style>
    <script>
        // Client-side: Warn/prevent non-letters on input (real-time UX)
        // Only letters and spaces (e.g., "New York"); auto-strip + alert for invalid
        function validateCityInput(input) {
            const validPattern = /^[A-Za-z ]*$/;  // Explicit space, no escape issues
            if (!validPattern.test(input.value)) {
                input.value = input.value.replace(/[^A-Za-z ]/g, '');  // Auto-strip invalid chars
                alert('Invalid character detected! City names can only contain letters and spaces (e.g., no numbers or special chars).');  // Warn user
                input.classList.add('invalid');
            } else {
                input.classList.remove('invalid');
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Weather Forecast</h1>
        <form method="post" action="/" onsubmit="return true;">
            <input type="text" name="city" placeholder="Enter city name (e.g., London)" required autofocus
                   pattern="[A-Za-z ]+" title="Only letters and spaces allowed (e.g., no numbers or special chars like ! or 123)"
                   oninput="validateCityInput(this)">
            <!-- Submit on Enter keypress; button for accessibility -->
            <button type="submit">Get Weather</button>
            <div class="input-hint">City names: letters and spaces only (e.g., "New York")</div>
        </form>
        {% if error %}
        <!-- Show warning for invalid input; no weather data generated -->
        <div class="error">Invalid input: '{{ error.city }}' contains numbers/special characters. Please enter only letters and spaces.</div>
        {% endif %}
        {% if weather is not none and weather %}
        <!-- Only display professional data for valid city (stricter Jinja check ensures no render on None/invalid) -->
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


def show_weather(city):
    """Display weather, temp, and suggestions for a city (core search logic)."""
    if not city:
        print("City name cannot be empty.")
        return None
    weather_data = generate_weather_data(city)
    print(f"\nThe weather in {weather_data['city']} is {weather_data['condition']} with a temperature of {weather_data['temperature']}°C.")
    print(f"Suggestions: Wear {weather_data['clothing']} and consider {weather_data['activity']}.\n")
    return weather_data


def show_favorites(data):
    """Option 3: Show favorite cities from JSON."""
    favorites = data.get("favorites", [])
    if favorites:
        print("\nFavorite Cities:")
        for city in favorites:
            print(f"- {city}")
    else:
        print("\nNo favorite cities yet.")
    print()


def show_history(data):
    """Option 4: Show search history (last 5 cities) from JSON."""
    history = data.get("search_history", [])
    if history:
        print("\nSearch History (last 5):")
        for city in history:
            print(f"- {city}")
    else:
        print("\nNo search history yet.")
    print()


def main():
    """
    Interactive CLI menu loop (as requested):
    [1] Search weather for a new city (auto-saves to history).
    [2] Add last searched city to favorites.
    [3] Show favorites.
    [4] Show search history.
    [5] Exit.
    Loads/saves JSON on start/change for persistence.
    """
    print("Welcome to the Weather App!")
    data = load_data()  # Load on startup
    last_searched = None

    while True:
        print("\nMain Menu:")
        print("[1] Search weather for a new city")
        print("[2] Add the last searched city to favorites")
        print("[3] Show favorite cities")
        print("[4] Show search history (last 5 cities)")
        print("[5] Exit the app")
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            # Search weather and update history
            city = input("Enter a city name: ").strip()
            weather_data = show_weather(city)
            if weather_data:
                data = add_to_history(data, city)  # Auto-save to history
                last_searched = city
                save_data(data)  # Save immediately
        elif choice == "2":
            # Add last to favorites
            if last_searched:
                data = add_to_favorites(data, last_searched)
                save_data(data)  # Save immediately
                print(f"Added '{last_searched}' to favorites.\n")
            else:
                print("No city searched yet. Use option 1 first.\n")
        elif choice == "3":
            # Show favorites
            show_favorites(data)
        elif choice == "4":
            # Show history
            show_history(data)
        elif choice == "5":
            # Exit
            print("Exiting the app. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-5.\n")


# Flask web app for the clean weather page (kept intact, no breaking changes)
# Run separately if needed by calling weather_page() logic or directly via app.run
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def weather_page():
    """
    Render the clean/professional weather page. Handles city input via form (submit on Enter).
    Added validation: City names only letters + spaces (client-side JS/HTML5 + server-side regex).
    - Invalid (numbers/special chars): Show warning, NO weather data generated.
    - Valid: Generate/display full data (temp, condition, suggestions, etc.) + retry capability via form.
    Web does not affect CLI/JSON features.
    """
    weather = None
    error = None
    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        if city:
            # Server-side validation: only letters and spaces (e.g., "New York" ok, "NYC123" or "NYC!" invalid)
            # Use explicit [A-Za-z ] for reliability (matches letters + space; ^$ anchors full string)
            if re.match(r'^[A-Za-z ]+$', city):
                # Valid: generate and display all data (temp, condition, suggestions, etc.)
                weather = generate_weather_data(city)
            else:
                # Invalid: warn user, do not provide weather/temp/suggestions
                error = {"city": city}
    # Pass to template for conditional rendering (error vs. weather data)
    # Use render_template_string for inline HTML/CSS (stricter {% if %} ensures clean separation)
    return render_template_string(WEATHER_PAGE_TEMPLATE, weather=weather, error=error)

if __name__ == "__main__":
    # Default: Run CLI menu loop (with JSON persistence).
    # For web page: comment above and use `app.run(debug=True, port=5001)` instead.
    # Access web at http://127.0.0.1:5001 if enabled.
    main()
