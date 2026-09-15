from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import LEAGUE_ID_TO_NAME
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.schemas.teams import ScheduleGame, TeamDetail, TeamSummary
from app.schemas.transactions import TransactionEvent
from app.services import standings_service
from app.services.espn_client import fetch_league_data, get_team_roster
from app.services.playoff_service import calculate_playoff_standings, get_ordinal
from app.services.schedule_service import get_team_schedule
from app.services.season_service import get_current_season
from app.services.standings_service import fetch_all_leagues, fetch_all_matchups, get_all_teams
from app.services.transactions_service import get_team_transactions

router = APIRouter(tags=["teams"])


@router.get("/teams", response_model=list[TeamSummary])
def teams():
    return get_all_teams()


@router.get("/teams/{league_id}/{team_id}", response_model=TeamDetail)
def team_detail(league_id: str, team_id: int):
    league_data = fetch_league_data(league_id)
    if not league_data or "teams" not in league_data:
        raise NotFoundError(f"League {league_id} not found")

    team = next((t for t in league_data["teams"] if t.get("id") == team_id), None)
    if not team:
        raise NotFoundError(f"Team {team_id} not found in league {league_id}")

    league_name = LEAGUE_ID_TO_NAME.get(league_id, "")
    team_name = team.get("name", "Unknown")
    record = team.get("record", {}).get("overall", {})

    playoff_standings = calculate_playoff_standings(fetch_all_leagues(), fetch_all_matchups())
    seed_row = next(
        (r for r in playoff_standings if r["team"]["team_name"] == team_name and r["team"]["league_name"] == league_name),
        None,
    )

    return TeamDetail(
        team=standings_service.team_ref(league_id, league_name, team_id, team_name),
        wins=record.get("wins", 0),
        losses=record.get("losses", 0),
        seed=get_ordinal(seed_row["rank"]) if seed_row else "N/A",
        logo=team.get("logo", ""),
        roster=get_team_roster(league_data, team_id),
    )


@router.get("/teams/{league_id}/{team_id}/schedule", response_model=list[ScheduleGame])
def team_schedule(league_id: str, team_id: int, db: Session = Depends(get_db)):
    return get_team_schedule(db, league_id, team_id, get_current_season())


@router.get("/teams/{league_id}/{team_id}/transactions", response_model=list[TransactionEvent])
def team_transactions(league_id: str, team_id: int):
    return get_team_transactions(league_id, team_id)
