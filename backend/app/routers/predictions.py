from fastapi import APIRouter, Query, HTTPException
from app.services.prediction_service import PredictionService

router = APIRouter()
service = PredictionService()


@router.get("/next")
def get_next_prediction(
    start_year: int = Query(default=2024),
    end_year: int = Query(default=2026),
):
    try:
        predictions = service.predict_from_history(
            start_year=start_year,
            end_year=end_year,
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Prediction failed: {error}",
        )

    return {
        "model": "baseline-history-v1",
        "training_years": {
            "start_year": start_year,
            "end_year": end_year,
        },
        "note": "Uses completed qualifying sessions only.",
        "count": len(predictions),
        "predictions": [prediction.__dict__ for prediction in predictions],
    }


@router.get("/race/{year}/{round_number}")
def get_race_prediction(
    year: int,
    round_number: int,
    start_year: int = Query(default=2024),
):
    try:
        predictions = service.predict_for_race(
            target_year=year,
            target_round=round_number,
            start_year=start_year,
            model_version="v1",
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Race prediction failed: {error}",
        )

    return {
        "model": "baseline-race-specific-v1",
        "target": {
            "year": year,
            "round": round_number,
        },
        "training_window": {
            "start_year": start_year,
            "end_before": {
                "year": year,
                "round": round_number,
            },
        },
        "count": len(predictions),
        "predictions": [prediction.__dict__ for prediction in predictions],
    }


@router.get("/{race_id}")
def get_prediction(
    race_id: str,
    start_year: int = Query(default=2024),
    end_year: int = Query(default=2026),
):
    try:
        predictions = service.predict_from_history(
            start_year=start_year,
            end_year=end_year,
            model_version="v1",
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Prediction failed: {error}",
        )

    return {
        "race_id": race_id,
        "model": "baseline-history-v1",
        "training_years": {
            "start_year": start_year,
            "end_year": end_year,
        },
        "note": "Uses completed qualifying sessions only.",
        "count": len(predictions),
        "predictions": [prediction.__dict__ for prediction in predictions],
    }