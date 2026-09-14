from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import LEAGUES
from app.db.session import get_db
from app.schemas.common import LeagueInfo
from app.services import matchup_service
from app.services.season_service import get_current_season
from app.services.standings_service import get_current_week

router = APIRouter(tags=["meta"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/current-week")
def current_week():
    return {"week": get_current_week()}


@router.get("/seasons")
def seasons(db: Session = Depends(get_db)):
    current = get_current_season()
    stored = matchup_service.list_seasons_with_data(db)
    fallback_range = list(range(2024, current + 2))
    all_seasons = sorted(set(stored) | set(fallback_range), reverse=True)
    return {"seasons": all_seasons, "current_season": current}


@router.get("/leagues", response_model=list[LeagueInfo])
def leagues():
    return [LeagueInfo(name=name, id=league_id) for name, league_id in LEAGUES.items()]
