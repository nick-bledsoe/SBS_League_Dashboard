from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.stats import WeeklyStats
from app.services.season_service import get_current_season
from app.services.weekly_stats_service import build_playoff_pairs, build_regular_season_pairs, calculate_weekly_stats

router = APIRouter(tags=["stats"])


@router.get("/weeks/{week}/stats", response_model=WeeklyStats)
def weekly_stats(
    week: int,
    phase: str = Query(default="regular", pattern="^(regular|playoff)$"),
    season: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if phase == "playoff":
        pairs = build_playoff_pairs(db, season or get_current_season(), week)
    else:
        pairs = build_regular_season_pairs(week)

    return calculate_weekly_stats(week, pairs)
