import os
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException

from app.routers.ai import clear_ai_response_cache
from app.services.feature_service import FeatureService

router = APIRouter()


@router.post("/refresh-data")
def refresh_data(
    x_admin_token: str | None = Header(default=None),
):
    expected_token = os.getenv("ADMIN_REFRESH_TOKEN")

    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_REFRESH_TOKEN is not configured",
        )

    if not x_admin_token or not secrets.compare_digest(
        x_admin_token,
        expected_token,
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid admin refresh token",
        )

    FeatureService.build_training_data.cache_clear()
    cleared_ai_entries = clear_ai_response_cache()

    return {
        "status": "refreshed",
        "message": (
            "Training-data and AI-response caches were cleared. "
            "The next forecast will rebuild using the latest available data."
        ),
        "cleared_ai_cache_entries": cleared_ai_entries,
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
    }