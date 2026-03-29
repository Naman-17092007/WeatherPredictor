import argparse
import requests
import sys

def get_coordinates(city_name):
    """
    Fetches the latitude and longitude for a given city name using the Open-Meteo Geocoding API.
    """
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    
    try:
        response = requests.get(url)
        # Raise an exception for HTTP errors (4xx, 5xx)
        response.raise_for_status() 
        # Parse the JSON response
        data = response.json()
        
        if 'results' in data and len(data['results']) > 0:
            result = data['results'][0]
            return result['latitude'], result['longitude'], result['name'], result.get('country', '')
        else:
            print(f"Error: Could not find coordinates for city '{city_name}'")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to geocoding API: {e}")
        return None

def get_weather_description(weathercode):
    if weathercode == 0:
        return "Clear sky"
    elif 1 <= weathercode <= 3:
        return "Mainly clear, partly cloudy, or overcast"
    elif 45 <= weathercode <= 48:
        return "Fog / depositing rime fog"
    elif 51 <= weathercode <= 55:
        return "Drizzle"
    elif 61 <= weathercode <= 65:
        return "Rain"
    elif 71 <= weathercode <= 77:
        return "Snow fall / Snow grains"
    elif 80 <= weathercode <= 82:
        return "Rain showers"
    elif 85 <= weathercode <= 86:
        return "Snow showers"
    elif 95 <= weathercode <= 99:
        return "Thunderstorm"
    return "Clear/Cloudy"

def get_weather(lat, lon):
    """
    Fetches the current weather and 7-day forecast for a given latitude and longitude.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if 'current_weather' in data and 'daily' in data:
            return data['current_weather'], data['daily']
        else:
            print("Error: Could not retrieve requested weather data.")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to weather API: {e}")
        return None, None

def display_weather(city, country, current_weather, daily_forecast):
    """
    Formats and prints the weather data and forecast to the terminal.
    """
    temp = current_weather.get('temperature', 'N/A')
    windspeed = current_weather.get('windspeed', 'N/A')
    winddirection = current_weather.get('winddirection', 'N/A')
    time_str = current_weather.get('time', 'N/A')
    
    weathercode = current_weather.get('weathercode', 0)
    weather_desc = get_weather_description(weathercode)

    print("\n" + "="*55)
    title = f"*** Weather for {city}, {country} ***" if country else f"*** Weather for {city} ***"
    print(title.center(55))
    print("="*55)
    print(f" Current Temperature : {temp} C")
    print(f" Condition           : {weather_desc}")
    print(f" Wind Speed          : {windspeed} km/h")
    print(f" Wind Direction      : {winddirection} deg")
    print(f" Last Updated        : {time_str.replace('T', ' ')}")
    print("-" * 55)
    print(" 7-DAY FORECAST".center(55))
    print("-" * 55)
    
    # Check if daily data exists and has length
    if daily_forecast and 'time' in daily_forecast:
        print(f" {'Date'.ljust(12)} | {'Max (C)'.ljust(8)} | {'Min (C)'.ljust(8)} | {'Condition'}")
        print("-" * 55)
        for i in range(len(daily_forecast['time'])):
            day = daily_forecast['time'][i]
            max_t = daily_forecast['temperature_2m_max'][i]
            min_t = daily_forecast['temperature_2m_min'][i]
            code = daily_forecast['weathercode'][i]
            cond = get_weather_description(code)
            # truncate condition to fit nicely
            cond = cond[:20] + "..." if len(cond) > 20 else cond
            print(f" {day.ljust(12)} | {str(max_t).ljust(8)} | {str(min_t).ljust(8)} | {cond}")
    else:
        print(" Forecast data unavailable.")
    print("="*55 + "\n")

def main():
    # Set up argument parser to receive city name from command line
    parser = argparse.ArgumentParser(description="Terminal Weather App using Open-Meteo API")
    parser.add_argument("city", type=str, nargs='*', help="Name of the city to get weather for", default=["London"])
    args = parser.parse_args()
    
    # Combine list of words into a single city string (e.g. "New York")
    target_city = " ".join(args.city)
    
    print(f"Fetching weather data for '{target_city}'...")
    
    # Step 1: Get Coordinates
    coords = get_coordinates(target_city)
    if not coords:
        sys.exit(1)
        
    lat, lon, city_name, country = coords
    
    # Step 2: Get Weather
    current_weather, daily_forecast = get_weather(lat, lon)
    if not current_weather:
        sys.exit(1)
        
    # Step 3: Display structured JSON output in a human-readable format
    display_weather(city_name, country, current_weather, daily_forecast)

if __name__ == "__main__":
    main()
