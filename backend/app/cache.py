"""TTL caches that replace Streamlit's st.cache_data for the ESPN client layer."""

from cachetools import TTLCache

# Keyed by league_id -> raw ESPN league JSON. Mirrors @st.cache_data(ttl=300) on fetch_league_data.
league_data_cache: TTLCache = TTLCache(maxsize=32, ttl=300)

# Keyed by (league_id, week) -> raw ESPN boxscore JSON. Same 300s TTL as league data.
boxscore_cache: TTLCache = TTLCache(maxsize=64, ttl=300)

# Single entry ("logos",) -> {abbr: logo_url}. Mirrors @st.cache_data(ttl=60) on fetch_nfl_logos.
nfl_logos_cache: TTLCache = TTLCache(maxsize=1, ttl=60)

# Single entry ("rankings",) -> aggregated player rankings list. This aggregation loops
# every league x every week played so far, so it's cached separately from the underlying
# per-week boxscore_cache to avoid redoing that work on every request.
player_rankings_cache: TTLCache = TTLCache(maxsize=1, ttl=300)
