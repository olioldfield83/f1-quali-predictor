from fastapi import APIRouter, Query, HTTPException
from app.services.odds_service import OddsService
from app.services.apisports_f1_service import APISportsF1Service

router = APIRouter()
odds_service = OddsService()
apisports_f1_service = APISportsF1Service()


@router.get("/sports")
def list_odds_sports():
    try:
        sports = odds_service.list_sports()
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Odds sports request failed: {error}",
        )

    return {
        "count": len(sports),
        "sports": sports,
    }


@router.get("/formula1/sports")
def find_formula1_sports():
    try:
        sports = odds_service.find_formula1_sports()
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Formula 1 sport lookup failed: {error}",
        )

    return {
        "count": len(sports),
        "sports": sports,
    }


@router.get("/formula1")
def get_formula1_odds(
    regions: str = Query(default="uk"),
    markets: str = Query(default="h2h"),
    odds_format: str = Query(default="decimal"),
):
    try:
        odds = odds_service.get_formula1_odds(
            regions=regions,
            markets=markets,
            odds_format=odds_format,
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Formula 1 odds request failed: {error}",
        )

    return {
        "regions": regions,
        "markets": markets,
        "odds_format": odds_format,
        "count": len(odds),
        "odds": odds,
    }


@router.get("/sport/{sport_key}")
def get_odds_for_sport_key(
    sport_key: str,
    regions: str = Query(default="uk"),
    markets: str = Query(default="h2h"),
    odds_format: str = Query(default="decimal"),
):
    try:
        events = odds_service._get(
            f"sports/{sport_key}/odds",
            {
                "regions": regions,
                "markets": markets,
                "oddsFormat": odds_format,
                "dateFormat": "iso",
            },
        )

        odds = odds_service.normalise_odds(
            sport_key=sport_key,
            events=events,
            regions=regions,
            markets=markets,
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Odds request for sport key '{sport_key}' failed: {error}",
        )

    return {
        "sport_key": sport_key,
        "regions": regions,
        "markets": markets,
        "odds_format": odds_format,
        "count": len(odds),
        "odds": odds,
    }


@router.get("/apisports/status")
def get_apisports_status():
    try:
        data = apisports_f1_service.status()
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"API-SPORTS status request failed: {error}",
        )

    return data


@router.get("/apisports/seasons")
def get_apisports_seasons():
    try:
        data = apisports_f1_service.seasons()
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"API-SPORTS seasons request failed: {error}",
        )

    return data


@router.get("/apisports/races")
def get_apisports_races(
    season: int = Query(default=2026),
):
    try:
        data = apisports_f1_service.races(season=season)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"API-SPORTS races request failed: {error}",
        )

    return data


@router.get("/apisports/drivers")
def get_apisports_drivers(
    search: str | None = Query(default=None),
):
    try:
        data = apisports_f1_service.drivers(search=search)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"API-SPORTS drivers request failed: {error}",
        )

    return data


@router.get("/apisports/teams")
def get_apisports_teams(
    search: str | None = Query(default=None),
):
    try:
        data = apisports_f1_service.teams(search=search)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"API-SPORTS teams request failed: {error}",
        )

    return data


@router.get("/apisports/rankings/drivers")
def get_apisports_driver_rankings(
    season: int = Query(default=2026),
):
    try:
        data = apisports_f1_service.rankings_drivers(season=season)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"API-SPORTS driver rankings request failed: {error}",
        )

    return data


@router.get("/apisports/rankings/teams")
def get_apisports_team_rankings(
    season: int = Query(default=2026),
):
    try:
        data = apisports_f1_service.rankings_teams(season=season)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"API-SPORTS team rankings request failed: {error}",
        )

    return data


@router.get("/apisports/raw")
def get_apisports_raw_endpoint(
    endpoint: str = Query(...),
    season: int | None = Query(default=None),
    race: int | None = Query(default=None),
    search: str | None = Query(default=None),
):
    try:
        data = apisports_f1_service.raw_endpoint(
            endpoint=endpoint,
            season=season,
            race=race,
            search=search,
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"API-SPORTS raw endpoint request failed: {error}",
        )

    return data