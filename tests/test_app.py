import unittest
from unittest.mock import Mock, patch

import requests

import app as weather_app


class WeatherAppTests(unittest.TestCase):
    def setUp(self):
        weather_app.app.config["TESTING"] = True
        self.client = weather_app.app.test_client()

    def test_empty_city_shows_validation_message(self):
        response = self.client.post("/", data={"city": "   "})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please enter a city name.", response.data)

    @patch("app.get_api_key", return_value="")
    def test_missing_api_key_shows_setup_message(self, _mock_key):
        response = self.client.post("/", data={"city": "London"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"OpenWeather API key is missing.", response.data)

    @patch("app.get_api_key", return_value="test-key")
    @patch("app.requests.get")
    def test_valid_city_searches_exact_query_and_renders_results(self, mock_get, _mock_key):
        mock_get.side_effect = [
            self._response(
                {
                    "name": "Paris",
                    "main": {
                        "temp": 18.4,
                        "feels_like": 17.8,
                        "humidity": 63,
                    },
                    "weather": [{"description": "clear sky", "icon": "01d"}],
                }
            ),
            self._response(
                {
                    "list": [
                        self._forecast_slot("2026-06-02 12:00:00", 18.2, "clear sky", 0.1),
                        self._forecast_slot("2026-06-02 15:00:00", 20.1, "clear sky", 0.0),
                        self._forecast_slot("2026-06-03 12:00:00", 16.7, "light rain", 0.7),
                    ]
                }
            ),
        ]

        response = self.client.post("/", data={"city": "Paris,FR"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Paris", response.data)
        self.assertIn(b"Should I bring an umbrella?", response.data)
        self.assertIn(b"Rain chance: 70%", response.data)
        self.assertEqual(mock_get.call_args_list[0].kwargs["params"]["q"], "Paris,FR")
        self.assertEqual(mock_get.call_args_list[1].kwargs["params"]["q"], "Paris,FR")

    @patch("app.get_api_key", return_value="test-key")
    @patch("app.requests.get", side_effect=requests.Timeout)
    def test_weather_request_failure_shows_friendly_error(self, _mock_get, _mock_key):
        response = self.client.post("/", data={"city": "London"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Could not reach the weather service.", response.data)

    @staticmethod
    def _response(payload, status_code=200):
        response = Mock()
        response.status_code = status_code
        response.ok = status_code < 400
        response.json.return_value = payload
        return response

    @staticmethod
    def _forecast_slot(dt_txt, temp, description, pop):
        return {
            "dt_txt": dt_txt,
            "main": {"temp": temp},
            "weather": [{"description": description}],
            "pop": pop,
        }


if __name__ == "__main__":
    unittest.main()
