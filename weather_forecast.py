import requests
import subprocess

class WeatherForecast:
    def __init__(self, office="MTR", x=85, y=105, user_agent="weather-script (your_email@gmail.com)"):
        self.office = office
        self.x = x
        self.y = y
        self.forecast_url = f"https://api.weather.gov/gridpoints/{self.office}/{self.x},{self.y}/forecast"
        self.headers = {
            "User-Agent": user_agent
        }
        self.detailed_forecast = ""

    def fetch_forecast(self):
        response = requests.get(self.forecast_url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch forecast. Status code: {response.status_code}")

        return response.json()

    def get_todays_detailed_forecast(self):
        data = self.fetch_forecast()
        periods = data.get("properties", {}).get("periods", [])

        detailed_forecast = ""
        for i in range(min(2, len(periods))):
            daily_forecast = periods[i]['name'] + ": " + periods[i]['detailedForecast'].replace(' mph', ' miles per hour') + " "
            detailed_forecast += daily_forecast
        return detailed_forecast
    
    def speak_todays_forecast(self):
        detailed_forecast = self.get_todays_detailed_forecast()
        p1 = subprocess.Popen(["bash", "-c", f"echo {detailed_forecast} | /home/atom/piper/piper/piper --model /home/atom/piper/en_US-danny-low.onnx --output_file /home/atom/piper/weather_forecast.mp3"])
        p1.wait()
        subprocess.Popen(["bash", "-c", "mpv /home/atom/piper/weather_forecast.mp3"])