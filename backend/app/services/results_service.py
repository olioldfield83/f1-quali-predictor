import fastf1
import pandas as pd
from pathlib import Path

CACHE_DIR = Path("cache/fastf1")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(str(CACHE_DIR))


class ResultsService:
    def get_qualifying_results(self, year: int, round_number: int) -> list[dict]:
        session = fastf1.get_session(year, round_number, "Q")
        session.load(laps=False, telemetry=False, weather=False, messages=False)

        results = session.results

        if results is None or results.empty:
            return []

        output = []

        for _, row in results.iterrows():
            position = row.get("Position")

            if pd.isna(position):
                continue

            output.append(
                {
                    "year": year,
                    "round": round_number,
                    "position": int(position),
                    "driver_number": str(row.get("DriverNumber")),
                    "broadcast_name": row.get("BroadcastName"),
                    "abbreviation": row.get("Abbreviation"),
                    "full_name": row.get("FullName"),
                    "team_name": row.get("TeamName"),
                    "q1": str(row.get("Q1")) if not pd.isna(row.get("Q1")) else None,
                    "q2": str(row.get("Q2")) if not pd.isna(row.get("Q2")) else None,
                    "q3": str(row.get("Q3")) if not pd.isna(row.get("Q3")) else None,
                }
            )

        return sorted(output, key=lambda item: item["position"])

    def get_multi_year_qualifying_results(
        self,
        start_year: int = 2024,
        end_year: int = 2026,
    ) -> list[dict]:
        all_results = []
        skipped_sessions = []

        for year in range(start_year, end_year + 1):
            try:
                schedule = fastf1.get_event_schedule(year)
            except Exception as error:
                skipped_sessions.append(
                    {
                        "year": year,
                        "round": None,
                        "reason": f"Could not load schedule: {error}",
                    }
                )
                continue

            for _, race in schedule.iterrows():
                round_number = int(race.get("RoundNumber"))

                # Skip testing/pre-season rows if present.
                if round_number <= 0:
                    continue

                try:
                    quali_results = self.get_qualifying_results(year, round_number)
                except Exception as error:
                    skipped_sessions.append(
                        {
                            "year": year,
                            "round": round_number,
                            "race_name": race.get("EventName"),
                            "reason": str(error),
                        }
                    )
                    continue

                for item in quali_results:
                    item["race_name"] = race.get("EventName")
                    item["country"] = race.get("Country")
                    item["location"] = race.get("Location")

                all_results.extend(quali_results)

        return all_results

    def get_multi_year_qualifying_summary(
        self,
        start_year: int = 2024,
        end_year: int = 2026,
    ) -> dict:
        results = self.get_multi_year_qualifying_results(
            start_year=start_year,
            end_year=end_year,
        )

        loaded_sessions = sorted(
            {
                (row["year"], row["round"], row.get("race_name"))
                for row in results
            }
        )

        latest_session = loaded_sessions[-1] if loaded_sessions else None

        return {
            "start_year": start_year,
            "end_year": end_year,
            "session_count": len(loaded_sessions),
            "row_count": len(results),
            "latest_loaded_session": {
                "year": latest_session[0],
                "round": latest_session[1],
                "race_name": latest_session[2],
            }
            if latest_session
            else None,
            "results": results,
        }