from fastapi import APIRouter, Query, HTTPException
from app.services.feature_service import FeatureService
from app.services.backtest_service import BacktestService

router = APIRouter()
feature_service = FeatureService()
backtest_service = BacktestService()


@router.get("/training-data")
def get_training_data(
    start_year: int = Query(default=2024),
    end_year: int = Query(default=2026),
):
    try:
        rows = feature_service.build_training_data(
            start_year=start_year,
            end_year=end_year,
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Training data build failed: {error}",
        )

    return {
        "start_year": start_year,
        "end_year": end_year,
        "count": len(rows),
        "rows": rows,
    }


@router.get("/backtest")
def get_backtest(
    year: int = Query(default=2025),
    start_year: int = Query(default=2024),
    model_version: str = Query(default="v2"),
):
    try:
        results = backtest_service.backtest_year(
            year=year,
            start_year=start_year,
            model_version=model_version,
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Backtest failed: {error}",
        )

    return results


@router.get("/compare")
def compare_models(
    year: int = Query(default=2025),
    start_year: int = Query(default=2024),
):
    try:
        results = backtest_service.compare_models(
            year=year,
            start_year=start_year,
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Model comparison failed: {error}",
        )

    return results


@router.get("/compare-summary")
def compare_models_summary(
    year: int = Query(default=2025),
    start_year: int = Query(default=2024),
):
    try:
        results = backtest_service.compare_models(
            year=year,
            start_year=start_year,
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Model comparison summary failed: {error}",
        )

    return {
        "year": results["year"],
        "start_year": results["start_year"],
        "winner": results["winner"],
        "mean_absolute_error_delta_v2_minus_v1": results[
            "mean_absolute_error_delta_v2_minus_v1"
        ],
        "summary": results["summary"],
    }