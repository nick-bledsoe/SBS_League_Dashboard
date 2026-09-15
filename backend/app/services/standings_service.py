from app.core.constants import LEAGUES, TEAM_OWNERS_BY_ID
from app.services.espn_client import fetch_league_data


def get_owner(league_name: str, team_id: int) -> str:
    return TEAM_OWNERS_BY_ID.get(league_name, {}).get(team_id, "")


def team_ref(league_id: str, league_name: str, team_id: int, team_name: str) -> dict:
    return {
        "league_id": league_id,
        "league_name": league_name,
        "team_id": team_id,
        "team_name": team_name,
        "owner": get_owner(league_name, team_id),
    }


def get_current_week() -> int:
    """Get current scoring period from any league."""
    for league_id in LEAGUES.values():
        league_data = fetch_league_data(league_id)
        if league_data and "scoringPeriodId" in league_data:
            return league_data["scoringPeriodId"]
    return 1


def get_team_score_for_week(league_id: str, team_name: str, week: int) -> float | None:
    """Get a specific team's score for a specific week."""
    league_data = fetch_league_data(league_id)
    if not league_data or "schedule" not in league_data:
        return None

    teams = league_data.get("teams", [])
    team_map = {team.get("id"): team.get("name", "Unknown") for team in teams}
    current_week = league_data.get("scoringPeriodId", 1)

    for matchup in league_data.get("schedule", []):
        if matchup.get("matchupPeriodId") != week:
            continue

        home = matchup.get("home", {})
        away = matchup.get("away", {})
        home_team_name = team_map.get(home.get("teamId"))
        away_team_name = team_map.get(away.get("teamId"))

        if home_team_name == team_name:
            side = home
        elif away_team_name == team_name:
            side = away
        else:
            continue

        if week == current_week:
            return round(side.get("totalPointsLive", 0), 1)
        return round(side.get("totalPoints", 0), 1)

    return None


def get_all_teams() -> list[dict]:
    """Get all teams from all leagues."""
    all_teams = []
    for league_name, league_id in LEAGUES.items():
        league_data = fetch_league_data(league_id)
        if league_data and "teams" in league_data:
            for team in league_data["teams"]:
                all_teams.append(
                    {
                        "team": team_ref(league_id, league_name, team.get("id"), team.get("name", "Unknown")),
                        "wins": team.get("record", {}).get("overall", {}).get("wins", 0),
                        "losses": team.get("record", {}).get("overall", {}).get("losses", 0),
                    }
                )
    return sorted(all_teams, key=lambda t: (t["team"]["league_name"], -t["wins"]))


def process_league_standings(data: dict, league_name: str) -> list[dict]:
    """Process league data into standings records."""
    if not data or "teams" not in data:
        return []

    teams_data = []
    for team in data["teams"]:
        record = team.get("record", {}).get("overall", {})
        streak_type = record.get("streakType", "")
        streak_length = record.get("streakLength", 0)
        streak = f"{streak_type[0].upper()}{streak_length}" if streak_type and streak_length > 0 else "-"

        team_name = team.get("name", "Unknown")
        teams_data.append(
            {
                "league": league_name,
                "team": team_ref(LEAGUES[league_name], league_name, team.get("id"), team_name),
                "wins": record.get("wins", 0),
                "losses": record.get("losses", 0),
                "points_for": record.get("pointsFor", 0),
                "points_against": record.get("pointsAgainst", 0),
                "transactions": team.get("transactionCounter", {}).get("acquisitions", 0),
                "streak": streak,
            }
        )
    return teams_data


def fetch_all_leagues() -> list[dict]:
    """Fetch and aggregate standings from all leagues, ranked globally and per-league."""
    all_teams: list[dict] = []
    for league_name, league_id in LEAGUES.items():
        league_data = fetch_league_data(league_id)
        if league_data:
            all_teams.extend(process_league_standings(league_data, league_name))

    if not all_teams:
        return []

    all_teams.sort(key=lambda t: (-t["wins"], -t["points_for"]))
    for idx, row in enumerate(all_teams, start=1):
        row["rank"] = idx
        row["points_for"] = round(row["points_for"], 1)
        row["points_against"] = round(row["points_against"], 1)

    league_counters: dict[str, int] = {}
    for row in all_teams:
        league_counters[row["league"]] = league_counters.get(row["league"], 0) + 1
        row["league_rank"] = league_counters[row["league"]]

    return all_teams


def process_matchups(data: dict, league_name: str) -> list[dict]:
    """Process matchup data for a league."""
    if not data or "schedule" not in data:
        return []

    teams = data.get("teams", [])
    current_week = data.get("scoringPeriodId", 1)
    team_map = {team.get("id"): team.get("name", "Unknown") for team in teams}
    logo_map = {team.get("id"): team.get("logo", "") for team in teams}
    league_id = LEAGUES[league_name]

    matchups = []
    for matchup in data.get("schedule", []):
        matchup_week = matchup.get("matchupPeriodId")
        home = matchup.get("home", {})
        away = matchup.get("away", {})
        if not away:
            continue

        home_team_id = home.get("teamId")
        away_team_id = away.get("teamId")

        if matchup_week == current_week:
            home_score = round(home.get("totalPointsLive", 0), 1)
            away_score = round(away.get("totalPointsLive", 0), 1)
        else:
            home_score = round(home.get("totalPoints", 0), 1)
            away_score = round(away.get("totalPoints", 0), 1)

        matchups.append(
            {
                "league_name": league_name,
                "week": matchup_week,
                "home": team_ref(league_id, league_name, home_team_id, team_map.get(home_team_id, "Unknown")),
                "home_logo": logo_map.get(home_team_id, ""),
                "home_score": home_score,
                "away": team_ref(league_id, league_name, away_team_id, team_map.get(away_team_id, "Unknown")),
                "away_logo": logo_map.get(away_team_id, ""),
                "away_score": away_score,
            }
        )
    return matchups


def fetch_all_matchups(week: int | None = None) -> list[dict]:
    """Fetch and aggregate matchups from all leagues, optionally filtered to one week."""
    all_matchups: list[dict] = []
    for league_name, league_id in LEAGUES.items():
        league_data = fetch_league_data(league_id)
        if league_data:
            all_matchups.extend(process_matchups(league_data, league_name))

    if week is not None:
        all_matchups = [m for m in all_matchups if m["week"] == week]

    return all_matchups
