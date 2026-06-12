from collections import defaultdict
from app.services.results_service import ResultsService


class FeatureService:
    def __init__(self):
        self.results_service = ResultsService()

    def build_training_data(self, start_year: int = 2024, end_year: int = 2026) -> list[dict]:
        results = self.results_service.get_multi_year_qualifying_results(
            start_year=start_year,
            end_year=end_year,
        )

        results = sorted(results, key=lambda x: (x["year"], x["round"], x["position"]))

        driver_history = defaultdict(list)
        team_history = defaultdict(list)
        training_rows = []

        for row in results:
            driver = row["abbreviation"]
            team = row["team_name"]
            position = row["position"]
            year = row["year"]
            round_number = row["round"]

            previous_driver_positions = driver_history[driver]
            previous_team_positions = team_history[team]

            team_driver_histories = {
                other_driver: history
                for other_driver, history in driver_history.items()
                if history and history[-1]["team"] == team and other_driver != driver
            }

            teammate_recent_values = []
            for _, teammate_history in team_driver_histories.items():
                teammate_positions = [
                    item["position"] for item in teammate_history[-3:]
                ]
                teammate_recent_values.extend(teammate_positions)

            if previous_driver_positions:
                driver_recent_positions = [
                    item["position"] for item in previous_driver_positions[-3:]
                ]
                driver_long_positions = [
                    item["position"] for item in previous_driver_positions[-8:]
                ]

                driver_recent_avg = sum(driver_recent_positions) / len(driver_recent_positions)
                driver_long_avg = sum(driver_long_positions) / len(driver_long_positions)
            else:
                driver_recent_avg = None
                driver_long_avg = None

            if previous_team_positions:
                team_recent_positions = [
                    item["position"] for item in previous_team_positions[-6:]
                ]
                team_long_positions = [
                    item["position"] for item in previous_team_positions[-16:]
                ]

                team_recent_avg = sum(team_recent_positions) / len(team_recent_positions)
                team_long_avg = sum(team_long_positions) / len(team_long_positions)
            else:
                team_recent_avg = None
                team_long_avg = None

            teammate_recent_avg = (
                sum(teammate_recent_values) / len(teammate_recent_values)
                if teammate_recent_values
                else None
            )

            teammate_gap = (
                driver_recent_avg - teammate_recent_avg
                if driver_recent_avg is not None and teammate_recent_avg is not None
                else None
            )

            q3_rate = (
                sum(1 for item in previous_driver_positions[-8:] if item["position"] <= 10)
                / len(previous_driver_positions[-8:])
                if previous_driver_positions
                else None
            )

            momentum = (
                driver_recent_avg - driver_long_avg
                if driver_recent_avg is not None and driver_long_avg is not None
                else None
            )

            training_rows.append(
                {
                    "year": year,
                    "round": round_number,
                    "race_name": row.get("race_name"),
                    "country": row.get("country"),
                    "location": row.get("location"),
                    "driver": driver,
                    "team": team,
                    "target_position": position,
                    "driver_recent_avg_position": driver_recent_avg,
                    "driver_long_avg_position": driver_long_avg,
                    "team_recent_avg_position": team_recent_avg,
                    "team_long_avg_position": team_long_avg,
                    "teammate_recent_avg_position": teammate_recent_avg,
                    "teammate_gap": teammate_gap,
                    "q3_rate": q3_rate,
                    "momentum": momentum,
                }
            )

            driver_history[driver].append(
                {
                    "year": year,
                    "round": round_number,
                    "team": team,
                    "position": position,
                }
            )

            team_history[team].append(
                {
                    "year": year,
                    "round": round_number,
                    "position": position,
                }
            )

        return training_rows