from fastapi import APIRouter

from app.schemas.standings import PlayoffStandingsRow, StandingsRow
from app.services.playoff_service import calculate_playoff_standings
from app.services.standings_service import fetch_all_leagues, fetch_all_matchups

router = APIRouter(tags=["standings"])


@router.get("/standings", response_model=list[StandingsRow])
def standings():
    return fetch_all_leagues()


@router.get("/standings/playoffs", response_model=list[PlayoffStandingsRow])
def playoff_standings():
    standings_rows = fetch_all_leagues()
    matchups = fetch_all_matchups()
    return calculate_playoff_standings(standings_rows, matchups)
