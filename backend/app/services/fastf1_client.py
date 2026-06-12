import fastf1
import pandas as pd
from pathlib import Path

CACHE_DIR = Path("cache/fastf1")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(str(CACHE_DIR))


class FastF1Client:
    def get_schedule(self, year: int) -> list[dict]:
        schedule = fastf1.get_event_schedule(year)

        races = []

        for _, row in schedule.iterrows():
            event_name = row.get("EventName")

            if pd.isna(event_name):
                continue

            races.append(
                {
                    "round": int(row.get("RoundNumber")),
                    "name": row.get("EventName"),
                    "country": row.get("Country"),
                    "location": row.get("Location"),
                    "official_name": row.get("OfficialEventName"),
                    "date": str(row.get("EventDate")),
                }
            )

        return races