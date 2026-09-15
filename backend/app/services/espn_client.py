import logging

import requests

from app.cache import boxscore_cache, league_data_cache, nfl_logos_cache
from app.core.constants import API_BASE_URL, BOXSCORE_API_URL, NFL_TEAMS
from app.core.errors import ESPNUpstreamError

logger = logging.getLogger(__name__)


def fetch_league_data(league_id: str) -> dict | None:
    """Fetch data from ESPN Fantasy Football API for a specific league. Cached 5 min."""
    if league_id in league_data_cache:
        return league_data_cache[league_id]

    url = API_BASE_URL.format(leagueId=league_id)
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise ESPNUpstreamError(f"Error fetching data for league {league_id}: {e}") from e

    league_data_cache[league_id] = data
    return data


def fetch_nfl_logos() -> dict[str, str]:
    """Fetch NFL team logos from ESPN API and cache them. Non-fatal on failure — degrades
    to an empty map rather than failing the whole request, since logos are cosmetic."""
    cached = nfl_logos_cache.get("logos")
    if cached is not None:
        return cached

    url = "https://site.web.api.espn.com/apis/site/v2/teams?region=us&lang=en&leagues=mlb%2Cnba%2Cnfl%2Cnhl%2Cwnba"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.warning("Could not fetch NFL logos: %s", e)
        return {}

    nfl_data = data.get("nfl", [])
    if not nfl_data:
        return {}

    logo_map: dict[str, str] = {}
    for division in nfl_data:
        for team in division.get("teams", []):
            abbr = team.get("abbreviation")
            logos = team.get("logos", [])
            logo_url = logos[0].get("href", "") if logos else ""
            if abbr and logo_url:
                logo_map[abbr] = logo_url

    nfl_logos_cache["logos"] = logo_map
    return logo_map


def get_nfl_logo(team_abbr: str) -> str:
    return fetch_nfl_logos().get(team_abbr, "")


def get_team_logo(league_id: str, team_id: int) -> str:
    league_data = fetch_league_data(league_id)
    if league_data and "teams" in league_data:
        for team in league_data["teams"]:
            if team.get("id") == team_id:
                return team.get("logo", "")
    return ""


def get_team_roster(data: dict, team_id: int) -> list[dict]:
    """Extract roster for a specific team with NFL team and positional ranking."""
    if not data:
        return []

    teams_data = data.get("draftDetail", {}).get("teams", []) or data.get("teams", [])

    for team in teams_data:
        if team.get("id") != team_id:
            continue

        players = []
        for entry in team.get("roster", {}).get("entries", []):
            player_pool_entry = entry.get("playerPoolEntry", {})
            player_info = player_pool_entry.get("player", {})
            player_name = player_info.get("fullName", "Unknown")
            player_id = player_info.get("id", "")
            lineup_slot_id = entry.get("lineupSlotId", 0)
            pro_team_id = player_info.get("proTeamId")
            nfl_team = NFL_TEAMS.get(pro_team_id, "N/A") if pro_team_id else "N/A"
            nfl_logo = get_nfl_logo(nfl_team) if nfl_team != "N/A" else ""
            ratings = player_pool_entry.get("ratings", {})
            positional_rank = ratings.get("0", {}).get("positionalRanking")

            if lineup_slot_id == 0:
                position, sort_order = "QB", 1
            elif lineup_slot_id == 17:
                position, sort_order = "K", 2
            elif lineup_slot_id == 18:
                position, sort_order = "P", 3
            else:
                position, sort_order = f"SLOT-{lineup_slot_id}", 99

            players.append(
                {
                    "player_id": str(player_id),
                    "name": player_name,
                    "position": position,
                    "nfl_team": nfl_team,
                    "nfl_logo": nfl_logo,
                    "positional_rank": str(positional_rank) if positional_rank else "-",
                    "sort_order": sort_order,
                }
            )

        players.sort(key=lambda p: p["sort_order"])
        return players

    return []


DEFAULT_POSITION_NAMES = {1: "QB", 5: "K", 7: "P"}


def get_player_bio(league_id: str, player_id: int) -> dict | None:
    """Find a player anywhere in a league's rosters and return bio info plus their
    actual (not projected) weekly points for every scoring period played so far."""
    league_data = fetch_league_data(league_id)
    if not league_data:
        return None

    for team in league_data.get("teams", []):
        for entry in team.get("roster", {}).get("entries", []):
            player_info = entry.get("playerPoolEntry", {}).get("player", {})
            if player_info.get("id") != player_id:
                continue

            pro_team_id = player_info.get("proTeamId")
            nfl_team = NFL_TEAMS.get(pro_team_id, "N/A") if pro_team_id else "N/A"

            weekly_points = [
                {"week": s["scoringPeriodId"], "points": round(s.get("appliedTotal", 0), 2)}
                for s in player_info.get("stats", [])
                # statSourceId 0 = actual (not projected); statSplitTypeId 1 = single week
                # (not a season/last-N aggregate); scoringPeriodId 0 means "season total".
                if s.get("statSourceId") == 0 and s.get("statSplitTypeId") == 1 and s.get("scoringPeriodId", 0) > 0
            ]
            weekly_points.sort(key=lambda w: w["week"])

            return {
                "player_id": str(player_id),
                "name": player_info.get("fullName", "Unknown"),
                "position": DEFAULT_POSITION_NAMES.get(player_info.get("defaultPositionId"), "UNKNOWN"),
                "nfl_team": nfl_team,
                "nfl_logo": get_nfl_logo(nfl_team) if nfl_team != "N/A" else "",
                "weekly_points": weekly_points,
            }

    return None


def parse_roster(roster_data: dict) -> list[dict]:
    """Parse roster entries into clean player data with points for a boxscore."""
    players = []
    for entry in roster_data.get("entries", []):
        player_pool = entry.get("playerPoolEntry", {})
        player_info = player_pool.get("player", {})

        stats = player_info.get("stats", [])
        points = round(stats[0].get("appliedTotal", 0), 2) if stats else 0

        default_position_id = player_info.get("defaultPositionId", 0)
        if default_position_id == 1:
            position = "QB"
        elif default_position_id == 5:
            position = "K"
        elif default_position_id == 7:
            position = "P"
        else:
            position = "UNKNOWN"

        pro_team_id = player_info.get("proTeamId")
        nfl_team = NFL_TEAMS.get(pro_team_id, "N/A") if pro_team_id else "N/A"

        players.append(
            {
                "player_id": str(player_info.get("id", "")),
                "name": player_info.get("fullName", "Unknown"),
                "position": position,
                "nfl_team": nfl_team,
                "points": points,
                "slot_id": entry.get("lineupSlotId", 0),
            }
        )

    position_order = {"QB": 0, "K": 1, "P": 2}
    players.sort(key=lambda p: (position_order.get(p["position"], 99), -p["points"]))
    return players


def get_matchup_roster_details(league_id: str, week: int) -> list[dict]:
    """Get detailed player-level scoring for all matchups in a week."""
    cache_key = (league_id, week)
    if cache_key in boxscore_cache:
        return boxscore_cache[cache_key]

    url = BOXSCORE_API_URL.format(leagueId=league_id, week=week)
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise ESPNUpstreamError(f"Error fetching matchup details for league {league_id}: {e}") from e

    teams = data.get("teams", [])
    team_map = {team.get("id"): team.get("name", "Unknown") for team in teams}
    logo_map = {team.get("id"): team.get("logo", "") for team in teams}
    # This response's own `scoringPeriodId` just echoes back the `week` query param we
    # sent, so it can't tell us whether `week` is actually in progress — ask the league's
    # own (unscoped) endpoint for that instead.
    league_data = fetch_league_data(league_id)
    current_week = (league_data or {}).get("scoringPeriodId", 1)
    # ESPN only finalizes `totalPoints` once a week completes; during an in-progress
    # week it stays 0 and the live score lives in `totalPointsLive` instead.
    points_field = "totalPointsLive" if week == current_week else "totalPoints"

    matchups = []
    for matchup in data.get("schedule", []):
        if matchup.get("matchupPeriodId") != week:
            continue

        home = matchup.get("home", {})
        away = matchup.get("away", {})
        if not away:
            continue

        home_team_id = home.get("teamId")
        away_team_id = away.get("teamId")

        matchups.append(
            {
                "week": week,
                "home_team": {
                    "id": home_team_id,
                    "name": team_map.get(home_team_id, "Unknown"),
                    "logo": logo_map.get(home_team_id, ""),
                    "total_points": round(home.get(points_field, 0), 1),
                    "roster": parse_roster(home.get("rosterForMatchupPeriod", {})),
                },
                "away_team": {
                    "id": away_team_id,
                    "name": team_map.get(away_team_id, "Unknown"),
                    "logo": logo_map.get(away_team_id, ""),
                    "total_points": round(away.get(points_field, 0), 1),
                    "roster": parse_roster(away.get("rosterForMatchupPeriod", {})),
                },
            }
        )

    boxscore_cache[cache_key] = matchups
    return matchups
