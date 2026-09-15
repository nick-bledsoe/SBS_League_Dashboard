import requests

from app.cache import player_directory_cache
from app.core.constants import LEAGUES, NFL_TEAMS
from app.services.espn_client import DEFAULT_POSITION_NAMES, get_matchup_roster_details
from app.services.standings_service import get_current_week

UNKNOWN_PLAYER = {"name": "Unknown Player", "position": "UNKNOWN", "nfl_team": "N/A"}

# Players endpoint ignores filterIds and just returns the whole pool regardless — a ~2.3MB
# one-time fetch, only used as a fallback for players never seen in any roster we scanned
# (e.g. added and dropped again before a boxscore snapshot ever captured them).
FULL_PLAYER_POOL_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/players?view=players_wl"


def get_player_directory() -> dict[str, dict]:
    """player_id -> {name, position, nfl_team}, built from every roster seen this season.

    A dropped player is a free agent by the time anything looks them up, so their name
    can't be resolved from any league's *current* roster — this assembles it instead from
    the same per-week roster snapshots player rankings already scans.
    """
    if "directory" in player_directory_cache:
        return player_directory_cache["directory"]

    current_week = get_current_week()
    directory: dict[str, dict] = {}

    for league_id in LEAGUES.values():
        for week in range(1, current_week + 1):
            for matchup in get_matchup_roster_details(league_id, week):
                for side in ("home_team", "away_team"):
                    for player in matchup[side]["roster"]:
                        player_id = player.get("player_id")
                        if player_id and player_id not in directory:
                            directory[player_id] = {
                                "name": player["name"],
                                "position": player["position"],
                                "nfl_team": player["nfl_team"],
                            }

    player_directory_cache["directory"] = directory
    return directory


def _get_full_player_pool() -> dict[str, dict]:
    if "full_pool" in player_directory_cache:
        return player_directory_cache["full_pool"]

    pool: dict[str, dict] = {}
    try:
        headers = {"X-Fantasy-Filter": '{"players":{"filterIds":{"value":[1]}}}'}
        response = requests.get(FULL_PLAYER_POOL_URL, headers=headers, timeout=20)
        response.raise_for_status()
        for p in response.json():
            pro_team_id = p.get("proTeamId")
            pool[str(p["id"])] = {
                "name": p.get("fullName", "Unknown"),
                "position": DEFAULT_POSITION_NAMES.get(p.get("defaultPositionId"), "UNKNOWN"),
                "nfl_team": NFL_TEAMS.get(pro_team_id, "N/A") if pro_team_id else "N/A",
            }
    except requests.exceptions.RequestException:
        pass  # Best-effort fallback — an unresolved name degrades to "Unknown Player", not a 500.

    player_directory_cache["full_pool"] = pool
    return pool


def resolve_player(player_id: str) -> dict:
    """Best-effort name/position/team for any player_id, roster-scanned directory first."""
    info = get_player_directory().get(player_id)
    if info:
        return {"player_id": player_id, **info}

    info = _get_full_player_pool().get(player_id)
    if info:
        return {"player_id": player_id, **info}

    return {"player_id": player_id, **UNKNOWN_PLAYER}
