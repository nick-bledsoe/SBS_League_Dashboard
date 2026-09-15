import logging

import requests

logger = logging.getLogger(__name__)

NEWS_API_URL = "https://site.api.espn.com/apis/fantasy/v3/games/ffl/news/players"


def get_player_news(player_id: int, days: int = 30) -> list[dict]:
    """Recent news/notes for a player. Non-fatal on failure — news is supplementary,
    so a hiccup here shouldn't break the player view that's asking for it."""
    try:
        response = requests.get(NEWS_API_URL, params={"days": days, "playerId": player_id}, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.warning("Could not fetch news for player %s: %s", player_id, e)
        return []

    feed = data.get("news", {}).get("feed", [])
    return [
        {
            "id": item.get("id"),
            "headline": item.get("headline", ""),
            "description": item.get("description", ""),
            "story": item.get("story", ""),
            "source": item.get("type", ""),
            "published": item.get("published", ""),
        }
        for item in feed
    ]
