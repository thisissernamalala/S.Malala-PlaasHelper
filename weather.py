import requests

def get_weather_data(start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": -33.9258,
        "longitude": 18.4232,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m",
        "timezone": "Africa/Cairo"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            'forecast': data['hourly']
        }
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None
