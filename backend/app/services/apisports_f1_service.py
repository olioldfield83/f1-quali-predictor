import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


class APISportsF1Service:
    def __init__(self):
        self.api_key = os.getenv("APISPORTS_KEY")
        self.base_url = os.getenv(
            "APISPORTS_F1_BASE_URL",
            "https://v1.formula-1.api-sports.io",
        ).rstrip("/")

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict:
        if not self.api_key:
            raise ValueError("APISPORTS_KEY is not configured")

        response = requests.get(
            f"{self.base_url}/{endpoint.lstrip('/')}",
            headers={
                "x-apisports-key": self.api_key,
            },
            params=params or {},
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def status(self) -> dict:
        return self._get("status")

    def seasons(self) -> dict:
        return self._get("seasons")

    def competitions(self) -> dict:
        return self._get("competitions")

    def circuits(self) -> dict:
        return self._get("circuits")

    def races(self, season: int | None = None) -> dict:
        params = {}
        if season:
            params["season"] = season
        return self._get("races", params)

    def drivers(self, search: str | None = None) -> dict:
        params = {}
        if search:
            params["search"] = search
        return self._get("drivers", params)

    def teams(self, search: str | None = None) -> dict:
        params = {}
        if search:
            params["search"] = search
        return self._get("teams", params)

    def rankings_drivers(self, season: int) -> dict:
        return self._get("rankings/drivers", {"season": season})

    def rankings_teams(self, season: int) -> dict:
        return self._get("rankings/teams", {"season": season})

    def raw_endpoint(
        self,
        endpoint: str,
        season: int | None = None,
        race: int | None = None,
        search: str | None = None,
    ) -> dict:
        """
        Exploratory helper so we can test undocumented/plan-specific endpoints
        such as odds-related paths without changing code each time.
        """
        params = {}

        if season is not None:
            params["season"] = season
        if race is not None:
            params["race"] = race
        if search:
            params["search"] = search

        return self._get(endpoint, params)
