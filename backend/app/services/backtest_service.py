from app.services.prediction_service import PredictionService
from app.services.results_service import ResultsService


class BacktestService:
    def __init__(self):
        self.prediction_service = PredictionService()
        self.results_service = ResultsService()

    def backtest_year(
        self,
        year: int,
        start_year: int = 2024,
        model_version: str = "v2",
    ) -> dict:
        all_actual_results = self.results_service.get_multi_year_qualifying_results(
            start_year=year,
            end_year=year,
        )

        rounds = sorted({row["round"] for row in all_actual_results})

        race_results = []

        total_absolute_error = 0
        total_predictions = 0
        pole_correct_count = 0
        top3_overlap_total = 0
        q3_overlap_total = 0
        race_count = 0

        for round_number in rounds:
            actual_rows = [
                row for row in all_actual_results
                if row["year"] == year and row["round"] == round_number
            ]

            if not actual_rows:
                continue

            predictions = self.prediction_service.predict_for_race(
                target_year=year,
                target_round=round_number,
                start_year=start_year,
                model_version=model_version,
            )

            if not predictions:
                continue

            actual_by_driver = {
                row["abbreviation"]: row["position"]
                for row in actual_rows
            }

            prediction_rows = []

            race_absolute_error = 0
            race_prediction_count = 0

            for prediction in predictions:
                if prediction.driver not in actual_by_driver:
                    continue

                actual_position = actual_by_driver[prediction.driver]
                error = abs(prediction.predicted_position - actual_position)

                race_absolute_error += error
                race_prediction_count += 1

                prediction_rows.append(
                    {
                        "driver": prediction.driver,
                        "team": prediction.team,
                        "predicted_position": prediction.predicted_position,
                        "actual_position": actual_position,
                        "absolute_error": error,
                        "score": prediction.score,
                    }
                )

            if race_prediction_count == 0:
                continue

            prediction_rows = sorted(
                prediction_rows,
                key=lambda item: item["predicted_position"],
            )

            actual_pole_driver = min(
                actual_rows,
                key=lambda row: row["position"],
            )["abbreviation"]

            predicted_pole_driver = prediction_rows[0]["driver"]

            pole_correct = predicted_pole_driver == actual_pole_driver

            if pole_correct:
                pole_correct_count += 1

            predicted_top3 = {
                row["driver"]
                for row in prediction_rows
                if row["predicted_position"] <= 3
            }

            actual_top3 = {
                row["abbreviation"]
                for row in actual_rows
                if row["position"] <= 3
            }

            predicted_q3 = {
                row["driver"]
                for row in prediction_rows
                if row["predicted_position"] <= 10
            }

            actual_q3 = {
                row["abbreviation"]
                for row in actual_rows
                if row["position"] <= 10
            }

            top3_overlap = len(predicted_top3 & actual_top3) / 3
            q3_overlap = len(predicted_q3 & actual_q3) / 10

            top3_overlap_total += top3_overlap
            q3_overlap_total += q3_overlap

            race_count += 1
            total_absolute_error += race_absolute_error
            total_predictions += race_prediction_count

            race_results.append(
                {
                    "year": year,
                    "round": round_number,
                    "race_name": actual_rows[0].get("race_name"),
                    "mean_absolute_error": round(
                        race_absolute_error / race_prediction_count,
                        3,
                    ),
                    "pole_correct": pole_correct,
                    "predicted_pole": predicted_pole_driver,
                    "actual_pole": actual_pole_driver,
                    "top3_overlap": round(top3_overlap, 3),
                    "q3_overlap": round(q3_overlap, 3),
                    "prediction_count": race_prediction_count,
                    "predictions": prediction_rows,
                }
            )

        overall_mae = (
            total_absolute_error / total_predictions
            if total_predictions
            else None
        )

        pole_accuracy = (
            pole_correct_count / race_count
            if race_count
            else None
        )

        top3_accuracy = (
            top3_overlap_total / race_count
            if race_count
            else None
        )

        q3_accuracy = (
            q3_overlap_total / race_count
            if race_count
            else None
        )

        return {
            "model": f"baseline-race-specific-{model_version}",
            "year": year,
            "start_year": start_year,
            "race_count": race_count,
            "prediction_count": total_predictions,
            "mean_absolute_error": round(overall_mae, 3) if overall_mae is not None else None,
            "pole_accuracy": round(pole_accuracy, 3) if pole_accuracy is not None else None,
            "top3_accuracy": round(top3_accuracy, 3) if top3_accuracy is not None else None,
            "q3_accuracy": round(q3_accuracy, 3) if q3_accuracy is not None else None,
            "races": race_results,
        }

    def compare_models(
        self,
        year: int,
        start_year: int = 2024,
    ) -> dict:
        v1 = self.backtest_year(
            year=year,
            start_year=start_year,
            model_version="v1",
        )

        v2 = self.backtest_year(
            year=year,
            start_year=start_year,
            model_version="v2",
        )

        v1_mae = v1["mean_absolute_error"]
        v2_mae = v2["mean_absolute_error"]

        mae_delta = (
            round(v2_mae - v1_mae, 3)
            if v1_mae is not None and v2_mae is not None
            else None
        )

        if mae_delta is None:
            winner = None
        elif mae_delta < 0:
            winner = "v2"
        elif mae_delta > 0:
            winner = "v1"
        else:
            winner = "tie"

        return {
            "year": year,
            "start_year": start_year,
            "winner": winner,
            "mean_absolute_error_delta_v2_minus_v1": mae_delta,
            "summary": {
                "v1": {
                    "mean_absolute_error": v1["mean_absolute_error"],
                    "pole_accuracy": v1["pole_accuracy"],
                    "top3_accuracy": v1["top3_accuracy"],
                    "q3_accuracy": v1["q3_accuracy"],
                },
                "v2": {
                    "mean_absolute_error": v2["mean_absolute_error"],
                    "pole_accuracy": v2["pole_accuracy"],
                    "top3_accuracy": v2["top3_accuracy"],
                    "q3_accuracy": v2["q3_accuracy"],
                },
            },
            "details": {
                "v1": v1,
                "v2": v2,
            },
        }