import os
from typing import Any
import requests
from dotenv import load_dotenv

load_dotenv()


class OddsService:
    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(self):
        self.api_key = os.getenv("THE_ODDS_API_KEY")

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        if not self.api_key:
            raise ValueError("THE_ODDS_API_KEY is not configured")

        request_params = params.copy() if params else {}
        request_params["apiKey"] = self.api_key

        response = requests.get(
            f"{self.BASE_URL}/{endpoint}",
            params=request_params,
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def list_sports(self) -> list[dict]:
        return self._get("sports", {})

    def find_formula1_sports(self) -> list[dict]:
        sports = self.list_sports()

        return [
            sport
            for sport in sports
            if "formula" in sport.get("title", "").lower()
            or "formula" in sport.get("key", "").lower()
            or "f1" in sport.get("title", "").lower()
            or "f1" in sport.get("key", "").lower()
        ]

    def get_formula1_sport_key(self) -> str:
        matches = self.find_formula1_sports()

        if not matches:
            raise ValueError(
                "No Formula 1 sport key found from The Odds API. "
                "Check whether F1 is currently available on your plan/region."
            )

        # Prefer an active sport if the API returns active status.
        active_matches = [
            sport for sport in matches if sport.get("active") is True
        ]

        selected = active_matches[0] if active_matches else matches[0]
        return selected["key"]

    def get_formula1_odds(
        self,
        regions: str = "uk",
        markets: str = "h2h",
        odds_format: str = "decimal",
    ) -> list[dict]:
        sport_key = self.get_formula1_sport_key()

        events = self._get(
            f"sports/{sport_key}/odds",
            {
                "regions": regions,
                "markets": markets,
                "oddsFormat": odds_format,
                "dateFormat": "iso",
            },
        )

        return self.normalise_odds(
            sport_key=sport_key,
            events=events,
            regions=regions,
            markets=markets,
        )

    def normalise_odds(
        self,
        sport_key: str,
        events: list[dict],
        regions: str,
        markets: str,
    ) -> list[dict]:
        normalised = []

        for event in events:
            event_id = event.get("id")
            event_name = event.get("home_team") or event.get("away_team") or event.get("sport_title")
            commence_time = event.get("commence_time")

            for bookmaker in event.get("bookmakers", []):
                bookmaker_key = bookmaker.get("key")
                bookmaker_title = bookmaker.get("title")

                for market in bookmaker.get("markets", []):
                    market_key = market.get("key")

                    for outcome in market.get("outcomes", []):
                        decimal_odds = outcome.get("price")

                        implied_probability = None
                        if isinstance(decimal_odds, (int, float)) and decimal_odds > 0:
                            implied_probability = 1 / decimal_odds

                        normalised.append(
                            {
                                "sport_key": sport_key,
                                "event_id": event_id,
                                "event_name": event_name,
                                "commence_time": commence_time,
                                "bookmaker_key": bookmaker_key,
                                "bookmaker": bookmaker_title,
                                "market": market_key,
                                "selection": outcome.get("name"),
                                "decimal_odds": decimal_odds,
                                "implied_probability": round(implied_probability, 4)
                                if implied_probability is not None
                                else None,
                                "regions": regions,
                                "requested_markets": markets,
                            }
                        )

        return normalised
