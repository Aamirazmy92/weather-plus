# Global Weather Dashboard

A simple Python web app for checking city weather anywhere in the world: current conditions, a 5-day forecast, and a logic-based "should I bring an umbrella?" recommendation.

Built as a portfolio project - small enough to explain clearly in a job interview.

## Live demo

_Add your Render URL here after deploying._

## Screenshot

_Add a screenshot of the results page here for your GitHub README._

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

## Deploy on Render (optional)

1. Push this repo to GitHub.
2. Create a new **Web Service** on Render and connect the repo.
3. Render can use the included `render.yaml`, or set manually:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
4. Add environment variable: `OPENWEATHER_API_KEY` = your API key.
5. Deploy and add the live URL to this README.

## Project structure

```text
app.py              # Routes, API calls, forecast aggregation, umbrella logic
templates/          # Jinja2 HTML templates
static/style.css    # Styling
requirements.txt    # Python dependencies
.env.example        # Template for API key (never commit .env)
```

## Interview talking points

- **End-to-end flow:** "The browser posts a city to Flask. Flask calls OpenWeatherMap with `requests`, parses JSON in Python, applies umbrella rules, and returns HTML from Jinja templates."
- **API integration:** "I use two endpoints - current weather and forecast - with the city query exactly as the user enters it, so searches can work worldwide."
- **Data processing:** "Forecast data comes in 3-hour chunks; I group by date and take min/max temperature and max rain probability per day."
- **Deliberate scope:** "No database or React - keeps the project easy to demo and maintain on a CV."

## Manual checks

- [ ] Home page loads with search form
- [ ] Valid city shows current weather, 5 days, and umbrella advice
- [ ] Empty city shows validation message
- [ ] Invalid city shows friendly error
- [ ] Missing API key shows clear setup message

## License

MIT - use freely for your portfolio.
