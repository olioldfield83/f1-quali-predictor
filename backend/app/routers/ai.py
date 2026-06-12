from fastapi import APIRouter, Query, HTTPException
from app.services.prediction_service import PredictionService
from app.services.ai_service import AIService

router = APIRouter()
prediction_service = PredictionService()
ai_service = AIService()


@router.get("/explain-next")
def explain_next_prediction(
    start_year: int = Query(default=2024),
    end_year: int = Query(default=2026),
    model_version: str = Query(default="v1"),
):
    try:
        predictions = prediction_service.predict_from_history(
            start_year=start_year,
            end_year=end_year,
            model_version=model_version,
        )

        prediction_dicts = [prediction.__dict__ for prediction in predictions]
        explanation = ai_service.explain_predictions(prediction_dicts)

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"AI explanation failed: {error}",
        )

    return {
        "prediction_model": f"baseline-history-{model_version}",
        "ai_model": ai_service.model,
        "count": len(prediction_dicts),
        "explanation": explanation,
        "predictions": prediction_dicts,
    }


@router.get("/explain-race/{year}/{round_number}")
def explain_race_prediction(
    year: int,
    round_number: int,
    start_year: int = Query(default=2024),
    model_version: str = Query(default="v1"),
):
    try:
        predictions = prediction_service.predict_for_race(
            target_year=year,
            target_round=round_number,
            start_year=start_year,
            model_version=model_version,
        )

        prediction_dicts = [prediction.__dict__ for prediction in predictions]
        explanation = ai_service.explain_predictions(prediction_dicts)

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"AI race explanation failed: {error}",
        )

    return {
        "prediction_model": f"baseline-race-specific-{model_version}",
        "target": {
            "year": year,
            "round": round_number,
        },
        "ai_model": ai_service.model,
        "count": len(prediction_dicts),
        "explanation": explanation,
        "predictions": prediction_dicts,
    }