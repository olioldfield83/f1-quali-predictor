import time
from fastapi import APIRouter, Query, HTTPException
from app.services.prediction_service import PredictionService
from app.services.ai_service import AIService

router = APIRouter()
prediction_service = PredictionService()
ai_service = AIService()

CACHE_TTL_SECONDS = 60 * 60  # 1 hour
_response_cache: dict[str, dict] = {}

def clear_ai_response_cache() -> int:
    count = len(_response_cache)
    _response_cache.clear()
    return count


def get_cached_response(cache_key: str) -> dict | None:
    cached = _response_cache.get(cache_key)

    if not cached:
        return None

    age_seconds = time.time() - cached["created_at"]

    if age_seconds > CACHE_TTL_SECONDS:
        _response_cache.pop(cache_key, None)
        return None

    return cached["data"]


def set_cached_response(cache_key: str, data: dict) -> None:
    _response_cache[cache_key] = {
        "created_at": time.time(),
        "data": data,
    }


@router.get("/explain-next")
def explain_next_prediction(
    start_year: int = Query(default=2024),
    end_year: int = Query(default=2026),
    model_version: str = Query(default="v1"),
):
    cache_key = f"explain-next:{start_year}:{end_year}:{model_version}"
    cached = get_cached_response(cache_key)

    if cached:
        return {
            **cached,
            "cached": True,
        }

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

    response = {
        "prediction_model": f"baseline-history-{model_version}",
        "ai_model": ai_service.model,
        "count": len(prediction_dicts),
        "explanation": explanation,
        "predictions": prediction_dicts,
        "cached": False,
    }

    set_cached_response(cache_key, response)

    return response


@router.get("/explain-race/{year}/{round_number}")
def explain_race_prediction(
    year: int,
    round_number: int,
    start_year: int = Query(default=2024),
    model_version: str = Query(default="v1"),
):
    cache_key = f"explain-race:{year}:{round_number}:{start_year}:{model_version}"
    cached = get_cached_response(cache_key)

    if cached:
        return {
            **cached,
            "cached": True,
        }

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

    response = {
        "prediction_model": f"baseline-race-specific-{model_version}",
        "target": {
            "year": year,
            "round": round_number,
        },
        "ai_model": ai_service.model,
        "count": len(prediction_dicts),
        "explanation": explanation,
        "predictions": prediction_dicts,
        "cached": False,
    }

    set_cached_response(cache_key, response)

    return response