from fastapi import APIRouter, Query, HTTPException
from app.services.fastf1_client import FastF1Client
from app.services.results_service import ResultsService

router = APIRouter()
client = FastF1Client()
results_service = ResultsService()


@router.get("/")
def list_races(year: int = Query(default=2026)):
    try:
        races = client.get_schedule(year=year)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"FastF1 schedule request failed: {error}",
        )

    return {
        "year": year,
        "count": len(races),
        "races": races,
    }


@router.get("/history/qualifying-results")
def get_historical_qualifying_results(
    start_year: int = Query(default=2024),
    end_year: int = Query(default=2026),
):
    try:
        results = results_service.get_multi_year_qualifying_results(
            start_year=start_year,
            end_year=end_year,
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"FastF1 historical qualifying request failed: {error}",
        )

    return {
        "start_year": start_year,
        "end_year": end_year,
        "count": len(results),
        "results": results,
    }


@router.get("/{round_number}/sessions")
def list_sessions(round_number: int, year: int = Query(default=2024)):
    sessions = [
        {"session_code": "FP1", "session_name": "Practice 1"},
        {"session_code": "FP2", "session_name": "Practice 2"},
        {"session_code": "FP3", "session_name": "Practice 3"},
        {"session_code": "Q", "session_name": "Qualifying"},
        {"session_code": "R", "session_name": "Race"},
    ]

    return {
        "year": year,
        "round_number": round_number,
        "sessions": sessions,
    }


@router.get("/{round_number}/qualifying-results")
def get_qualifying_results(
    round_number: int,
    year: int = Query(default=2024),
):
    try:
        results = results_service.get_qualifying_results(
            year=year,
            round_number=round_number,
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"FastF1 qualifying results request failed: {error}",
        )

    return {
        "year": year,
        "round_number": round_number,
        "count": len(results),
        "results": results,
    }