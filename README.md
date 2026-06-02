# weather-plus

A simple Python web app for checking city weather anywhere in the world: current conditions, a 5-day forecast, and a logic-based "should I bring an umbrella?" recommendation.

## Screenshots

<img width="1919" height="923" alt="image" src="https://github.com/user-attachments/assets/9e16c7c3-03ae-4a7d-9c24-ddb151c4203a" />
<img width="906" height="899" alt="image" src="https://github.com/user-attachments/assets/b8830ffc-7b0c-42fe-a4ea-9dc46780cbda" />


## Tech stack

| Layer | Technology |
|-------|------------|
| Language | Python |
| Web framework | Flask |
| Weather data | [OpenWeatherMap API](https://openweathermap.org/api) (free tier) |
| Frontend | HTML + CSS (server-rendered with Jinja2) |
| Deploy (optional) | [Render](https://render.com) |

## How it works

1. User enters a city on the home page and submits the form.
2. Flask calls OpenWeatherMap twice: current weather and 5-day forecast (3-hour intervals).
3. Python parses the JSON, groups forecast slots into one row per day, and runs umbrella rules.
4. Results are rendered as HTML - no React or separate frontend build.

For ambiguous city names, users can include a country code, such as `Paris,FR` or `London,GB`.

## Umbrella logic

The app recommends an umbrella when any of these are true:

- Current conditions mention rain, drizzle, shower, or thunderstorm.
- Today or tomorrow has rain probability (`pop`) of 40% or higher.
- Today or tomorrow's forecast description mentions rain-related weather.

These thresholds are simple business rules you can explain and adjust in `app.py`.

## Local setup

### Prerequisites

- Python 3.10+
- Free [OpenWeatherMap API key](https://home.openweathermap.org/api_keys) (activation can take a few minutes)

### Run locally

```bash
cd Weather+
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set your key:

```text
OPENWEATHER_API_KEY=your_actual_key
```

Start the app:

```bash
flask --app app run
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) and search for a city, such as London, Paris, Tokyo, or New York.

## Project structure

```text
app.py              # Routes, API calls, forecast aggregation, umbrella logic
templates/          # Jinja2 HTML templates
static/style.css    # Styling
requirements.txt    # Python dependencies
.env                # API key 
```

## License

MIT — see [LICENSE](LICENSE) in this repository.
