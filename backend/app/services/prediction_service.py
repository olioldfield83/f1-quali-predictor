from dataclasses import dataclass
from collections import defaultdict
from app.services.feature_service import FeatureService


@dataclass
class DriverPrediction:
    driver: str
    team: str
    predicted_position: int
    score: float
    driver_recent_avg_position: float | None
    driver_long_avg_position: float | None
    team_recent_avg_position: float | None
    team_long_avg_position: float | None
    teammate_gap: float | None
    momentum: float | None
    q3_rate: float | None
    pole_probability: float
    q3_probability: float
    confidence: str


class PredictionService:
    def __init__(self):
        self.feature_service = FeatureService()

    def _score_v1(
        self,
        driver_recent: float,
        driver_long: float,
        team_recent: float,
        team_long: float,
        teammate_gap: float,
        momentum: float,
        q3_rate: float,
    ) -> float:
        return (
            0.45 * driver_recent
            + 0.20 * driver_long
            + 0.25 * team_recent
            + 0.10 * team_long
            - 2.00 * q3_rate
        )

    def _score_v2(
        self,
        driver_recent: float,
        driver_long: float,
        team_recent: float,
        team_long: float,
        teammate_gap: float,
        momentum: float,
        q3_rate: float,
    ) -> float:
        return (
            0.35 * driver_recent
            + 0.15 * driver_long
            + 0.20 * team_recent
            + 0.10 * team_long
            + 0.10 * teammate_gap
            + 0.10 * momentum
            - 1.80 * q3_rate
        )

    def _build_predictions_from_rows(
        self,
        rows: list[dict],
        limit_to_latest_grid: bool = True,
        model_version: str = "v2",
    ) -> list[DriverPrediction]:
        if not rows:
            return []

        latest_year = max(row["year"] for row in rows)
        latest_round = max(row["round"] for row in rows if row["year"] == latest_year)

        latest_grid = [
            row for row in rows
            if row["year"] == latest_year and row["round"] == latest_round
        ]

        active_drivers = {row["driver"] for row in latest_grid}

        driver_rows = defaultdict(list)

        for row in rows:
            driver_rows[row["driver"]].append(row)

        prediction_inputs = []

        for driver, history in driver_rows.items():
            if limit_to_latest_grid and driver not in active_drivers:
                continue

            latest = history[-1]
            team = latest["team"]

            driver_recent = latest.get("driver_recent_avg_position")
            driver_long = latest.get("driver_long_avg_position")
            team_recent = latest.get("team_recent_avg_position")
            team_long = latest.get("team_long_avg_position")
            teammate_gap = latest.get("teammate_gap")
            momentum = latest.get("momentum")
            q3_rate = latest.get("q3_rate")

            driver_recent = driver_recent if driver_recent is not None else 12.0
            driver_long = driver_long if driver_long is not None else driver_recent
            team_recent = team_recent if team_recent is not None else 12.0
            team_long = team_long if team_long is not None else team_recent
            teammate_gap = teammate_gap if teammate_gap is not None else 0.0
            momentum = momentum if momentum is not None else 0.0
            q3_rate = q3_rate if q3_rate is not None else 0.4

            if model_version == "v1":
                score = self._score_v1(
                    driver_recent=driver_recent,
                    driver_long=driver_long,
                    team_recent=team_recent,
                    team_long=team_long,
                    teammate_gap=teammate_gap,
                    momentum=momentum,
                    q3_rate=q3_rate,
                )
            elif model_version == "v2":
                score = self._score_v2(
                    driver_recent=driver_recent,
                    driver_long=driver_long,
                    team_recent=team_recent,
                    team_long=team_long,
                    teammate_gap=teammate_gap,
                    momentum=momentum,
                    q3_rate=q3_rate,
                )
            else:
                raise ValueError(f"Unsupported model_version: {model_version}")

            prediction_inputs.append(
                {
                    "driver": driver,
                    "team": team,
                    "score": score,
                    "driver_recent_avg_position": driver_recent,
                    "driver_long_avg_position": driver_long,
                    "team_recent_avg_position": team_recent,
                    "team_long_avg_position": team_long,
                    "teammate_gap": teammate_gap,
                    "momentum": momentum,
                    "q3_rate": q3_rate,
                }
            )

        prediction_inputs = sorted(prediction_inputs, key=lambda item: item["score"])

        output = []

        for index, item in enumerate(prediction_inputs, start=1):
            pole_probability = max(0.01, 0.32 - (index - 1) * 0.035)

            q3_probability = max(
                0.03,
                min(
                    0.98,
                    item["q3_rate"] * 0.70 + (1 / max(index, 1)) * 0.30,
                ),
            )

            confidence = "medium" if index <= 5 or item["q3_rate"] >= 0.6 else "low"

            output.append(
                DriverPrediction(
                    driver=item["driver"],
                    team=item["team"],
                    predicted_position=index,
                    score=round(item["score"], 3),
                    driver_recent_avg_position=round(item["driver_recent_avg_position"], 2),
                    driver_long_avg_position=round(item["driver_long_avg_position"], 2),
                    team_recent_avg_position=round(item["team_recent_avg_position"], 2),
                    team_long_avg_position=round(item["team_long_avg_position"], 2),
                    teammate_gap=round(item["teammate_gap"], 2),
                    momentum=round(item["momentum"], 2),
                    q3_rate=round(item["q3_rate"], 3),
                    pole_probability=round(pole_probability, 3),
                    q3_probability=round(q3_probability, 3),
                    confidence=confidence,
                )
            )

        return output

    def predict_from_history(
        self,
        start_year: int = 2024,
        end_year: int = 2026,
        limit_to_latest_grid: bool = True,
        model_version: str = "v2",
    ) -> list[DriverPrediction]:
        rows = self.feature_service.build_training_data(
            start_year=start_year,
            end_year=end_year,
        )

        return self._build_predictions_from_rows(
            rows=rows,
            limit_to_latest_grid=limit_to_latest_grid,
            model_version=model_version,
        )

    def predict_for_race(
        self,
        target_year: int,
        target_round: int,
        start_year: int = 2024,
        model_version: str = "v2",
    ) -> list[DriverPrediction]:
        rows = self.feature_service.build_training_data(
            start_year=start_year,
            end_year=target_year,
        )

        historical_rows = [
            row for row in rows
            if (row["year"] < target_year)
            or (row["year"] == target_year and row["round"] < target_round)
        ]

        return self._build_predictions_from_rows(
            rows=historical_rows,
            limit_to_latest_grid=True,
            model_version=model_version,
        )