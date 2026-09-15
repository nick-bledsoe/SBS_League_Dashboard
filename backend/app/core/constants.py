# League configurations
LEAGUES = {
    "Doinks": "1629152724",
    "Shanks": "464845016",
    "Clunks": "112677575",
}

LEAGUE_ID_TO_NAME = {league_id: name for name, league_id in LEAGUES.items()}

API_BASE_URL = (
    "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/segments/0/"
    "leagues/{leagueId}?view=mLiveScoring&view=mMatchupScore&view=mRoster&view=mSettings"
    "&view=mStandings&view=mStatus&view=mTeam&view=modular&view=mNav&view=mDraftDetail"
    "&platformVersion=ea036b729b6388bc4495a4b40c151e1a7dc80106"
)

BOXSCORE_API_URL = (
    "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/segments/0/"
    "leagues/{leagueId}?scoringPeriodId={week}&view=mBoxscore&view=mMatchupScore&view=mRoster"
    "&view=mSettings&view=mStatus&view=mTeam&view=modular&view=mNav"
    "&platformVersion=f23636631f3d5609b41daa409faa6f587135a0fb"
)

# The `transactions` field only shows up when mTransactions2 is combined with these other
# views (mTransactions2 alone silently omits it) — found by inspecting what ESPN's own
# recent-activity page requests, not documented anywhere.
TRANSACTIONS_API_URL = (
    "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/segments/0/"
    "leagues/{leagueId}?scoringPeriodId={week}&view=mDraftDetail&view=mStatus&view=mSettings"
    "&view=mTeam&view=mTransactions2&view=modular&view=mNav"
)

# NFL Team ID mapping
NFL_TEAMS = {
    2: "BUF", 15: "MIA", 17: "NE", 20: "NYJ",
    33: "BAL", 4: "CIN", 5: "CLE", 23: "PIT",
    34: "HOU", 11: "IND", 30: "JAX", 10: "TEN",
    7: "DEN", 12: "KC", 13: "LV", 24: "LAC",
    6: "DAL", 19: "NYG", 21: "PHI", 28: "WSH",
    3: "CHI", 8: "DET", 9: "GB", 16: "MIN",
    1: "ATL", 29: "CAR", 18: "NO", 27: "TB",
    22: "ARI", 14: "LAR", 25: "SF", 26: "SEA",
}

# Team (league, ESPN team_id) -> Owner Name. Keyed by team_id (not name) because
# managers keep renaming their teams mid-season — team_id is the stable ESPN
# identifier that survives a rename, unlike team_name which broke this mapping
# three separate times before switching to this.
TEAM_OWNERS_BY_ID: dict[str, dict[int, str]] = {
    "Doinks": {
        1: "Carl",
        2: "Jason",
        3: "Matt",
        4: "Mark",
        5: "John",
        6: "Paul",
    },
    "Shanks": {
        1: "Anthony",
        2: "Al",
        3: "Nick",
        4: "CJ",
        5: "Noah",
        6: "Conor",
    },
    "Clunks": {
        1: "Brian",
        2: "Po",
        3: "Jace",
        4: "Kyle",
        5: "Mikey",
        6: "Jackson",
    },
}

MATCHUP_TYPES = [
    "Quarterfinal",
    "Semifinal",
    "3rd Place",
    "Championship",
]

MATCHUP_TYPE_COLORS = {
    "Quarterfinal": "#ffd700",
    "Semifinal": "#ff6b6b",
    "3rd Place": "#4ecdc4",
    "Championship": "#9b59b6",
}
