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

# Team Name to Owner Name mapping
TEAM_OWNERS = {
    "Ray Finkle": "Jason",
    "SMAUX": "Po",
    "Booters": "Anthony",
    "The Slye Dawgs": "Jackson",
    "Kicking Me Softly": "Conor",
    "Coffin Corner": "CJ",
    "Team C": "John",
    "Blair Walsh Project": "Nick",
    "Help Me Step Burrow": "Paul",
    "Michael's Magnificent Team": "Mikey",
    "mark's Magnificent Team": "Mark",
    "Noah's Nifty Team": "Noah",
    "Al's Astounding Team": "Al",
    "Kyle's Top-Notch Team": "Kyle",
    "Burnin Rubbers": "Matt",
    "Turf Toe": "Carl",
    "Jace": "Jace",
    "Lets Get Reicharded": "Brian",
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
