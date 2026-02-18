import random
import json
import os
import re  # For city name validation (letters/spaces only)
from flask import Flask, request, render_template_string, session  # Added session for temp unit toggle (C/F)

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


# JSON persistence for favorites, search history, and temp_unit (C/F toggle) (as requested)
JSON_FILE = "favorites.json"
# DEFAULT_DATA extended for temp_unit; load_data handles defaults
DEFAULT_DATA = {"favorites": [], "search_history": [], "temp_unit": "C"}


def load_data():
    """Load favorites, search_history, and temp_unit (C/F) from JSON file on startup. Create defaults if not exists."""
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r") as f:
                data = json.load(f)
                # Ensure structure, limit history to last 5, default temp_unit='C'
                data.setdefault("favorites", [])
                data.setdefault("search_history", [])
                data.setdefault("temp_unit", "C")
                data["search_history"] = data["search_history"][:5]
                return data
        except (json.JSONDecodeError, IOError):
            pass  # Fall back to defaults on error
    # DEFAULT_DATA extended for new feature
    return {**DEFAULT_DATA, "temp_unit": "C"}.copy()


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


# Helpers for C/F toggle (new feature)
def celsius_to_fahrenheit(temp_c):
    """Convert Celsius to Fahrenheit for toggle display."""
    return round(temp_c * 9 / 5 + 32, 1)


def toggle_temp_unit(data):
    """Toggle between C and F in data (persisted to JSON); returns updated data and current unit."""
    data["temp_unit"] = "F" if data.get("temp_unit", "C") == "C" else "C"
    return data, data["temp_unit"]


def get_display_temp(temp_c, unit):
    """Return temp string with unit (C or F conversion)."""
    if unit == "F":
        return f"{celsius_to_fahrenheit(temp_c)}°F"
    return f"{temp_c}°C"


# Update JSON helpers to support temp_unit persistence (C/F toggle state)
# (extends load_data/save_data without breaking CLI; DEFAULT_DATA updated implicitly)


# Unified inline HTML template for the full web app (simple/professional interface incorporating all features)
# - Search form with validation (letters/spaces only).
# - C/F toggle, weather results (with suggestions/temp), favorites, history.
# - Buttons for actions; reads/writes favorites.json.
WEATHER_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather App - Full Features</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f0f8ff; color: #333; margin: 0; padding: 20px; display: flex; justify-content: center; min-height: 100vh; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 600px; width: 100%; }
        h1, h2 { color: #2c3e50; }
        form { margin-bottom: 20px; }
        input[type="text"] { padding: 10px; width: 60%; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; }
        input.invalid { border-color: #e74c3c; }
        button { padding: 10px 20px; background-color: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 5px; }
        button:hover { background-color: #2980b9; }
        button.danger { background-color: #e74c3c; }
        button.danger:hover { background-color: #c0392b; }
        .section { background: #e8f4f8; padding: 15px; border-radius: 8px; margin: 15px 0; text-align: left; }
        .error { color: #e74c3c; background: #fdf2f2; padding: 10px; border-radius: 5px; margin: 10px 0; font-weight: bold; }
        .input-hint { font-size: 12px; color: #777; margin-top: 5px; }
        ul { list-style: none; padding: 0; }
        li { margin: 5px 0; }
        footer { margin-top: 20px; font-size: 12px; color: #777; text-align: center; }
    </style>
    <script>
        // Client-side validation: only letters/spaces; auto-strip + alert for invalid chars
        function validateCityInput(input) {
            const validPattern = /^[A-Za-z ]*$/;
            if (!validPattern.test(input.value)) {
                input.value = input.value.replace(/[^A-Za-z ]/g, '');
                alert('Invalid character! Only letters and spaces (e.g., "New York").');
                input.classList.add('invalid');
            } else {
                input.classList.remove('invalid');
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Weather App</h1>
        <!-- C/F Toggle (new feature, persisted in JSON) -->
        <form method="post" action="/">
            <input type="hidden" name="action" value="toggle_temp">
            <button type="submit">Toggle Temp: {{ temp_unit }}°</button>
        </form>
        <!-- City Search Form (with validation) -->
        <form method="post" action="/" onsubmit="return true;">
            <input type="hidden" name="action" value="search">
            <input type="text" name="city" placeholder="Enter city name (e.g., London)" required autofocus
                   pattern="[A-Za-z ]+" title="Only letters and spaces allowed (no numbers/special chars)"
                   oninput="validateCityInput(this)">
            <button type="submit">Get Weather</button>
            <div class="input-hint">Letters and spaces only (e.g., "New York")</div>
        </form>
        {% if error %}
        <!-- Validation warning: no weather data for invalid -->
        <div class="error">Invalid input: '{{ error.city }}' - only letters/spaces allowed. No data generated.</div>
        {% endif %}
        {% if weather %}
        <!-- Weather results with suggestions and display temp (C/F) -->
        <div class="section">
            <h2>Weather for {{ weather.city }}</h2>
            <p><strong>Condition:</strong> {{ weather.condition }}</p>
            <p><strong>Temperature:</strong> {{ display_temp }}</p>
            <p><strong>Suggestion:</strong> Wear {{ weather.clothing }} and consider {{ weather.activity }}.</p>
            <form method="post" action="/">
                <input type="hidden" name="action" value="add_fav">
                <input type="hidden" name="city" value="{{ weather.city }}">
                <button type="submit">Add to Favorites</button>
            </form>
        </div>
        {% endif %}
        <!-- Favorites section -->
        <div class="section">
            <h2>Favorites</h2>
            {% if favorites %}
            <ul>
                {% for city in favorites %}
                <li>{{ city }}</li>
                {% endfor %}
            </ul>
            {% else %}
            <p>No favorites yet.</p>
            {% endif %}
        </div>
        <!-- Search history section (last 5) -->
        <div class="section">
            <h2>Search History (Last 5)</h2>
            {% if history %}
            <ul>
                {% for city in history %}
                <li>{{ city }}</li>
                {% endfor %}
            </ul>
            {% else %}
            <p>No history yet.</p>
            {% endif %}
            <form method="post" action="/">
                <input type="hidden" name="action" value="clear_history">
                <button type="submit" class="danger">Clear History</button>
            </form>
        </div>
        <footer>Powered by Flask | Persistence: favorites.json | Temp: {{ temp_unit }}</footer>
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


# Unified Flask web app incorporating all features:
# - Weather search + suggestions + validation.
# - C/F temp toggle (persisted).
# - Favorites + search history (via favorites.json).
# - Simple inline HTML interface.
# - Defaults to server at http://localhost:5000 (CLI available via main()).
# App reads/writes favorites.json for persistence.
app = Flask(__name__)
app.secret_key = "weather_app_secret"  # For session if extended; not heavily used here

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main web interface at http://localhost:5000.
    Handles search, actions (toggle, add_fav, clear_history) via POST; renders all data.
    Uses inline template for simplicity; integrates weather, suggestions, favs/history, validation.
    """
    data = load_data()  # Load from favorites.json on every request
    weather = None
    error = None
    display_temp = None
    temp_unit = data.get("temp_unit", "C")

    if request.method == 'POST':
        action = request.form.get('action')
        city = request.form.get('city', '').strip()

        if action == 'search' or request.form.get('city'):  # Search weather
            if city:
                # Validation: only letters/spaces; warn if invalid, no data
                if re.match(r'^[A-Za-z ]+$', city):
                    weather = generate_weather_data(city)  # Includes suggestions
                    # Temp display based on unit
                    display_temp = get_display_temp(weather['temperature'], temp_unit)
                    # Auto-add to history, save to JSON
                    data = add_to_history(data, city)
                    save_data(data)
                else:
                    # Invalid: warning, no weather/suggestions
                    error = {"city": city}
        elif action == 'toggle_temp':  # C/F toggle
            data, temp_unit = toggle_temp_unit(data)
            save_data(data)  # Persist unit
            if weather:  # Recompute display if result active
                display_temp = get_display_temp(weather['temperature'], temp_unit)
        elif action == 'add_fav' and city:  # Add to favorites
            data = add_to_favorites(data, city)
            save_data(data)
        elif action == 'clear_history':  # Clear history
            data["search_history"] = []
            save_data(data)

    # Render simple HTML with all data (favs, history, conditional results/error)
    # Pass vars for template
    return render_template_string(
        WEATHER_PAGE_TEMPLATE,
        weather=weather,
        error=error,
        display_temp=display_temp,
        favorites=data.get("favorites", []),
        history=data.get("search_history", []),
        temp_unit=temp_unit
    )

# Keep original CLI menu accessible (e.g., python -c "from weather_app import main; main()")
# Web is now primary for localhost view.

if __name__ == "__main__":
    # Run web server for localhost:5000 (all features).
    # Use 0.0.0.0 for accessibility; debug=True for dev.
    # CLI/favs/JSON intact.
    app.run(host="127.0.0.1", port=5000, debug=True)
