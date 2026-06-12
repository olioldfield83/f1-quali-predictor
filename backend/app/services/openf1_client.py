import requests
from typing import Any


class OpenF1Client:
    BASE_URL = "https://api.openf1.org/v1"

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> list[dict]:
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_meetings(self, year: int | None = None) -> list[dict]:
        params = {}
        if year:
            params["year"] = year
        return self._get("meetings", params)

    def get_sessions(self, meeting_key: int | None = None, year: int | None = None) -> list[dict]:
        params = {}
        if meeting_key:
            params["meeting_key"] = meeting_key
        if year:
            params["year"] = year
        return self._get("sessions", params)

    def get_drivers(self, session_key: int) -> list[dict]:
        return self._get("drivers", {"session_key": session_key})

    def get_laps(self, session_key: int) -> list[dict]:
        return self._get("laps", {"session_key": session_key})

    def get_weather(self, session_key: int) -> list[dict]:
        return self._get("weather", {"session_key": session_key})
