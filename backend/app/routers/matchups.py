from fastapi import APIRouter, Query

from app.core.constants import LEAGUE_ID_TO_NAME
from app.schemas.matchups import BoxscoreMatchup, RegularMatchup
from app.services import standings_service
from app.services.espn_client import get_matchup_roster_details
from app.services.standings_service import fetch_all_matchups

router = APIRouter(tags=["matchups"])


@router.get("/matchups", response_model=list[RegularMatchup])
def matchups(week: int | None = Query(default=None)):
    """Regular-season matchups. Omit `week` to get every week (used for the home page's
    weekly-high-scores section and week selector), or pass it to filter to one week."""
    return fetch_all_matchups(week)


@router.get("/matchups/{league_id}/{week}/boxscore", response_model=list[BoxscoreMatchup])
def boxscore(league_id: str, week: int):
    league_name = LEAGUE_ID_TO_NAME.get(league_id, "")
    raw_matchups = get_matchup_roster_details(league_id, week)

    result = []
    for m in raw_matchups:
        home, away = m["home_team"], m["away_team"]
        result.append(
            {
                "week": m["week"],
                "home": {
                    "team": standings_service.team_ref(league_id, league_name, home["id"], home["name"]),
                    "logo": home["logo"],
                    "total_points": home["total_points"],
                    "roster": home["roster"],
                },
                "away": {
                    "team": standings_service.team_ref(league_id, league_name, away["id"], away["name"]),
                    "logo": away["logo"],
                    "total_points": away["total_points"],
                    "roster": away["roster"],
                },
            }
        )
    return result
