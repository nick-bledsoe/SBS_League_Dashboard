import logging

import requests

logger = logging.getLogger(__name__)

STATS_API_URL = "https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/athletes/{player_id}/stats"


def get_player_stats(player_id: int) -> list[dict]:
    """Real (not fantasy-scoring) NFL stats by category and season, e.g. a kicker's
    field goals made/attempted per distance range. Non-fatal on failure — this is
    supplementary detail, not core to the player view that's requesting it."""
    try:
        response = requests.get(STATS_API_URL.format(player_id=player_id), timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.warning("Could not fetch stats for player %s: %s", player_id, e)
        return []

    teams = data.get("teams", {})
    team_names_by_id = {team["id"]: team.get("displayName", "") for team in teams.values()}

    categories = []
    for category in data.get("categories", []):
        seasons = []
        for row in category.get("statistics", []):
            seasons.append(
                {
                    "year": row.get("season", {}).get("year"),
                    "team": team_names_by_id.get(row.get("teamId"), ""),
                    "values": row.get("stats", []),
                }
            )
        seasons.sort(key=lambda s: s["year"] or 0, reverse=True)

        if seasons:
            categories.append(
                {
                    "name": category.get("name", ""),
                    "display_name": category.get("displayName", ""),
                    "labels": [label.strip() for label in category.get("labels", [])],
                    "seasons": seasons,
                }
            )

    return categories
