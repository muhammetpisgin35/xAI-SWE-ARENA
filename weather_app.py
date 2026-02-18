import random

def main():
    # Ask the user for a city name
    city = input("Enter a city name: ").strip()
    
    # List of possible weather conditions
    weather_conditions = [
        "Sunny", "Rainy", "Cloudy", "Windy", 
        "Snowy", "Foggy", "Stormy", "Clear",
        "Overcast", "Partly Cloudy"
    ]
    
    # Generate random weather condition
    condition = random.choice(weather_conditions)
    
    # Generate random temperature between -5 and 35 inclusive
    temperature = random.randint(-5, 35)
    
    # Print the result
    print(f"The weather in {city} is {condition} with a temperature of {temperature}°C.")

if __name__ == "__main__":
    main()
