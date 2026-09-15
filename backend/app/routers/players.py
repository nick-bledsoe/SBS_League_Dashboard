from fastapi import APIRouter, Query

from app.core.errors import NotFoundError
from app.schemas.players import PlayerDetail, PlayerRanking
from app.services.espn_client import get_player_bio
from app.services.news_service import get_player_news
from app.services.player_rankings_service import get_player_rankings
from app.services.player_stats_service import get_player_stats

router = APIRouter(tags=["players"])


# Declared before /players/{player_id} so "rankings" isn't swallowed by that dynamic route.
@router.get("/players/rankings", response_model=list[PlayerRanking])
def player_rankings():
    return get_player_rankings()


@router.get("/players/{player_id}", response_model=PlayerDetail)
def player_detail(player_id: int, league_id: str = Query(...)):
    """Combined player popup data: bio, actual weekly points so far this season,
    recent news, and real (non-fantasy) NFL stats by season. league_id is required
    since a player's applied fantasy points reflect that league's own scoring
    settings."""
    bio = get_player_bio(league_id, player_id)
    if not bio:
        raise NotFoundError(f"Player {player_id} not found in league {league_id}")

    return {**bio, "news": get_player_news(player_id), "stats": get_player_stats(player_id)}
