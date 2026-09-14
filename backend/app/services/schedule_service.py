from sqlalchemy.orm import Session

from app.core.constants import LEAGUE_ID_TO_NAME
from app.db.models import Matchup
from app.services import standings_service
from app.services.espn_client import fetch_league_data, get_team_logo
from app.services.standings_service import get_team_score_for_week


def _regular_season_games(league_id: str, league_name: str, team_id: int) -> list[dict]:
    league_data = fetch_league_data(league_id)
    if not league_data or "schedule" not in league_data:
        return []

    teams = league_data.get("teams", [])
    team_map = {t.get("id"): t.get("name", "Unknown") for t in teams}
    logo_map = {t.get("id"): t.get("logo", "") for t in teams}
    current_week = league_data.get("scoringPeriodId", 1)

    games = []
    for matchup in league_data["schedule"]:
        home = matchup.get("home", {})
        away = matchup.get("away", {})
        if not away:
            continue

        home_team_id = home.get("teamId")
        away_team_id = away.get("teamId")
        if team_id not in (home_team_id, away_team_id):
            continue

        week = matchup.get("matchupPeriodId")
        is_home = home_team_id == team_id
        mine, theirs = (home, away) if is_home else (away, home)
        opponent_id = away_team_id if is_home else home_team_id

        if week == current_week:
            team_score = round(mine.get("totalPointsLive", 0), 1)
            opp_score = round(theirs.get("totalPointsLive", 0), 1)
        else:
            team_score = round(mine.get("totalPoints", 0), 1)
            opp_score = round(theirs.get("totalPoints", 0), 1)

        if week <= current_week:
            if team_score > opp_score:
                result, color = "W", "#3eab43"
            elif team_score < opp_score:
                result, color = "L", "#d32f2f"
            else:
                result, color = "T", "#666"
        else:
            result, color, team_score, opp_score = "-", "#666", None, None

        games.append(
            {
                "week": week,
                "opponent": standings_service.team_ref(
                    league_id, league_name, opponent_id, team_map.get(opponent_id, "Unknown")
                ),
                "opponent_logo": logo_map.get(opponent_id, ""),
                "location": "vs" if is_home else "@",
                "result": result,
                "result_color": color,
                "team_score": team_score,
                "opp_score": opp_score,
                "is_current": week == current_week,
                "game_type": "Regular Season",
            }
        )
    return games


def _playoff_games(db: Session, league_id: str, team_id: int, season: int, current_week: int) -> list[dict]:
    games = []
    for matchup in db.query(Matchup).filter(Matchup.season == season).all():
        mine = next((p for p in matchup.participants if p.league_id == league_id and p.team_id == team_id), None)
        if not mine:
            continue
        opponent = next(p for p in matchup.participants if p is not mine)

        team_score = get_team_score_for_week(mine.league_id, mine.team_name, matchup.week)
        opp_score = get_team_score_for_week(opponent.league_id, opponent.team_name, matchup.week)

        if matchup.week <= current_week and team_score is not None and opp_score is not None:
            if team_score > opp_score:
                result, color = "W", "#3eab43"
            elif team_score < opp_score:
                result, color = "L", "#d32f2f"
            else:
                result, color = "T", "#666"
        else:
            result, color, team_score, opp_score = "-", "#666", None, None

        games.append(
            {
                "week": matchup.week,
                "opponent": standings_service.team_ref(
                    opponent.league_id, opponent.league_name, opponent.team_id, opponent.team_name
                ),
                "opponent_logo": get_team_logo(opponent.league_id, opponent.team_id),
                "location": "vs",
                "result": result,
                "result_color": color,
                "team_score": team_score,
                "opp_score": opp_score,
                "is_current": matchup.week == current_week,
                "game_type": matchup.round_type or "Playoff",
            }
        )
    return games


def get_team_schedule(db: Session, league_id: str, team_id: int, season: int) -> list[dict]:
    league_name = LEAGUE_ID_TO_NAME.get(league_id, "")
    league_data = fetch_league_data(league_id)
    current_week = league_data.get("scoringPeriodId", 1) if league_data else 1

    games = _regular_season_games(league_id, league_name, team_id)
    games.extend(_playoff_games(db, league_id, team_id, season, current_week))
    games.sort(key=lambda g: g["week"])
    return games
