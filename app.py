import os
from collections import defaultdict
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)

app = Flask(__name__)


def get_api_key():
    return os.getenv("OPENWEATHER_API_KEY")


CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


class WeatherError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def _check_api_key():
    api_key = get_api_key()
    if not api_key or api_key == "your_key_here":
        raise WeatherError(
            "OpenWeather API key is missing. Copy .env.example to .env and add your key."
        )


def _get_params(city):
    return {"q": city, "units": "metric", "appid": get_api_key()}


def _api_error_message(response):
    try:
        data = response.json()
        api_message = data.get("message", "")
    except ValueError:
        api_message = ""

    if response.status_code == 401:
        return (
            "Invalid OpenWeather API key. Log in at openweathermap.org/api_keys, "
            "copy the key exactly into .env, or generate a new one. New keys can take "
            "up to 2 hours to activate after signup."
        )
    if response.status_code == 429:
        return "Too many requests. Please wait a minute and try again."
    if api_message:
        return f"Weather service error: {api_message}"
    return "Weather service is unavailable. Please try again later."


def _get_weather_json(url, city):
    try:
        response = requests.get(url, params=_get_params(city), timeout=10)
    except requests.RequestException:
        raise WeatherError(
            "Could not reach the weather service. Check your connection and try again."
        )

    if response.status_code == 404:
        raise WeatherError(f'Could not find "{city}". Try another city name.')
    if not response.ok:
        raise WeatherError(_api_error_message(response))

    try:
        return response.json()
    except ValueError:
        raise WeatherError("Weather service returned an invalid response. Please try again.")


def fetch_current(city):
    data = _get_weather_json(CURRENT_URL, city)
    try:
        return {
            "city_name": data["name"],
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "description": data["weather"][0]["description"].title(),
            "humidity": data["main"]["humidity"],
            "icon": data["weather"][0]["icon"],
        }
    except (KeyError, IndexError, TypeError):
        raise WeatherError("Weather service returned incomplete current weather data.")


def fetch_forecast(city):
    data = _get_weather_json(FORECAST_URL, city)

    by_date = defaultdict(list)
    try:
        for item in data["list"]:
            date = item["dt_txt"].split(" ")[0]
            by_date[date].append(item)
    except (KeyError, TypeError):
        raise WeatherError("Weather service returned incomplete forecast data.")

    days = []
    for date in sorted(by_date.keys())[:5]:
        slots = by_date[date]
        try:
            temps = [slot["main"]["temp"] for slot in slots]
            pops = [slot.get("pop", 0) for slot in slots]
            descriptions = [slot["weather"][0]["description"] for slot in slots]
        except (KeyError, IndexError, TypeError):
            raise WeatherError("Weather service returned incomplete forecast data.")

        days.append(
            {
                "date": date,
                "temp_min": round(min(temps)),
                "temp_max": round(max(temps)),
                "description": max(set(descriptions), key=descriptions.count).title(),
                "pop": max(pops),
            }
        )
    return days


def umbrella_advice(current, forecast_days):
    rain_words = ("rain", "drizzle", "shower", "thunderstorm")
    current_desc = current["description"].lower()

    if any(word in current_desc for word in rain_words):
        return True, "Yes - rain is expected right now. Bring an umbrella."

    for day in forecast_days[:2]:
        if day["pop"] >= 0.4:
            return True, "Yes - rain is likely today or tomorrow. Bring an umbrella."
        if any(word in day["description"].lower() for word in rain_words):
            return True, "Yes - rain is likely today or tomorrow. Bring an umbrella."

    return False, "No - looks dry for now. You probably do not need an umbrella."


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    city = request.form.get("city", "").strip()
    if not city:
        return render_template("index.html", error="Please enter a city name.")

    try:
        _check_api_key()
        current = fetch_current(city)
        forecast = fetch_forecast(city)
        bring_umbrella, umbrella_message = umbrella_advice(current, forecast)
        return render_template(
            "results.html",
            current=current,
            forecast=forecast,
            bring_umbrella=bring_umbrella,
            umbrella_message=umbrella_message,
            city_query=city,
        )
    except WeatherError as error:
        return render_template("index.html", error=error.message, city=city)


if __name__ == "__main__":
    app.run(debug=True)
