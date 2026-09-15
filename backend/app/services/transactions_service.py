import requests

from app.cache import transactions_cache
from app.core.constants import LEAGUE_ID_TO_NAME, LEAGUES, TRANSACTIONS_API_URL
from app.core.errors import ESPNUpstreamError
from app.services import standings_service
from app.services.espn_client import fetch_league_data
from app.services.player_directory_service import resolve_player
from app.services.standings_service import get_current_week

# DRAFT and ROSTER (lineup slot moves) aren't roster activity in the sense anyone cares
# about here; TRADE_PROPOSAL/VETO/DECLINE/ERROR never actually happened.
RELEVANT_TYPES = {"WAIVER", "FREEAGENT", "TRADE_ACCEPT"}


def _fetch_raw_transactions(league_id: str, week: int) -> list[dict]:
    cache_key = (league_id, week)
    if cache_key in transactions_cache:
        return transactions_cache[cache_key]

    url = TRANSACTIONS_API_URL.format(leagueId=league_id, week=week)
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise ESPNUpstreamError(f"Error fetching transactions for league {league_id}: {e}") from e

    txns = [
        t
        for t in data.get("transactions", [])
        if t.get("type") in RELEVANT_TYPES and t.get("status") == "EXECUTED"
    ]
    transactions_cache[cache_key] = txns
    return txns


def get_week_transactions(week: int, league_id: str | None = None) -> list[dict]:
    """Every add/drop/trade executed in a given week, newest first.

    A single transaction (especially a trade) can carry multiple items, and a week can
    have any number of transactions — this flattens neither away, it just resolves each
    item's player and team into something the frontend can render directly.
    """
    league_ids = [league_id] if league_id else list(LEAGUES.values())

    events = []
    for lid in league_ids:
        league_name = LEAGUE_ID_TO_NAME.get(lid, lid)
        league_data = fetch_league_data(lid)
        team_names = {t.get("id"): t.get("name", "Unknown") for t in (league_data or {}).get("teams", [])}

        for txn in _fetch_raw_transactions(lid, week):
            items = []
            for item in txn.get("items", []):
                to_team_id = item.get("toTeamId", 0)
                from_team_id = item.get("fromTeamId", 0)
                action = "ADD" if to_team_id else "DROP"
                team_id = to_team_id or from_team_id
                items.append(
                    {
                        "action": action,
                        "team": standings_service.team_ref(lid, league_name, team_id, team_names.get(team_id, "Unknown")),
                        "player": resolve_player(str(item.get("playerId"))),
                    }
                )
            events.append(
                {
                    "id": txn["id"],
                    "type": txn["type"],
                    "week": week,
                    "date": txn.get("processDate") or txn.get("proposedDate") or 0,
                    "items": items,
                }
            )

    events.sort(key=lambda e: e["date"], reverse=True)
    return events


def get_team_transactions(league_id: str, team_id: int) -> list[dict]:
    """Every add/drop/trade a team has been party to this season, newest first."""
    events = []
    for week in range(1, get_current_week() + 1):
        for event in get_week_transactions(week, league_id):
            if any(item["team"]["team_id"] == team_id for item in event["items"]):
                events.append(event)

    events.sort(key=lambda e: e["date"], reverse=True)
    return events


def get_week_transaction_highlights(week: int) -> dict:
    """Most-added and most-dropped player league-wide for a given week, with who did it."""
    added: dict[str, dict] = {}
    dropped: dict[str, dict] = {}

    for event in get_week_transactions(week):
        for item in event["items"]:
            bucket = added if item["action"] == "ADD" else dropped
            player_id = item["player"]["player_id"]
            entry = bucket.setdefault(player_id, {"player": item["player"], "count": 0, "by": []})
            entry["count"] += 1
            entry["by"].append(item["team"])

    most_added = max(added.values(), key=lambda e: e["count"], default=None)
    most_dropped = max(dropped.values(), key=lambda e: e["count"], default=None)
    return {"week": week, "most_added": most_added, "most_dropped": most_dropped}
