import requests
import pandas as pd
import streamlit as st

# League configurations
LEAGUES = {
    "Doinks": "1629152724",
    "Shanks": "464845016",
    "Clunks": "112677575"
}

API_BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/{leagueId}?view=mLiveScoring&view=mMatchupScore&view=mRoster&view=mSettings&view=mStandings&view=mStatus&view=mTeam&view=modular&view=mNav&view=mDraftDetail&platformVersion=ea036b729b6388bc4495a4b40c151e1a7dc80106"

# NFL Team ID mapping
NFL_TEAMS = {
    2: "BUF", 15: "MIA", 17: "NE", 20: "NYJ",
    33: "BAL", 4: "CIN", 5: "CLE", 23: "PIT",
    34: "HOU", 11: "IND", 30: "JAX", 10: "TEN",
    7: "DEN", 12: "KC", 13: "LV", 24: "LAC",
    6: "DAL", 19: "NYG", 21: "PHI", 28: "WSH",
    3: "CHI", 8: "DET", 9: "GB", 16: "MIN",
    1: "ATL", 29: "CAR", 18: "NO", 27: "TB",
    22: "ARI", 14: "LAR", 25: "SF", 26: "SEA"
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
    "Blaire Walsh Project": "Nick",
    "Help Me Step Burrow": "Paul",
    "Michael's Magnificent Team": "Mikey",
    "mark's Monstrous Team": "Mark",
    "Big Legs, bigger hearts": "Noah",
    "Graham Guano": "Al",
    "Kyle's Top-Notch Team": "Kyle",
    "Matt's ": "Matt",
    "Turf Toe": "Carl",
    "Tory Taylor #19": "Jace",
    "Lets Get Reicharded": "Brian"
}

# Cache for NFL team logos
_NFL_LOGOS_CACHE = None


def fetch_nfl_logos():
    """Fetch NFL team logos from ESPN API and cache them"""
    global _NFL_LOGOS_CACHE

    if _NFL_LOGOS_CACHE is not None:
        return _NFL_LOGOS_CACHE

    try:
        url = "https://site.web.api.espn.com/apis/site/v2/teams?region=us&lang=en&leagues=mlb%2Cnba%2Cnfl%2Cnhl%2Cwnba"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # The data structure has 'nfl' as a direct key with divisions
        nfl_data = data.get('nfl', [])

        if not nfl_data:
            return {}

        # Build mapping of team abbreviation to logo URL
        logo_map = {}
        # nfl_data is a list of divisions
        for division in nfl_data:
            teams = division.get('teams', [])
            for team in teams:
                abbr = team.get('abbreviation')
                # Get the first logo from the logos array
                logos = team.get('logos', [])
                logo_url = logos[0].get('href', '') if logos else ''
                if abbr and logo_url:
                    logo_map[abbr] = logo_url

        _NFL_LOGOS_CACHE = logo_map
        return logo_map

    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch NFL logos: {e}")
        return {}


def get_nfl_logo(team_abbr):
    """Get the logo URL for an NFL team abbreviation"""
    logos = fetch_nfl_logos()
    return logos.get(team_abbr, '')


def fetch_league_data(league_id):
    """Fetch data from ESPN Fantasy Football API for a specific league"""
    try:
        url = API_BASE_URL.format(leagueId=league_id)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data for league {league_id}: {e}")
        return None


def get_current_week():
    """Get current scoring period from any league"""
    for league_id in LEAGUES.values():
        league_data = fetch_league_data(league_id)
        if league_data and 'scoringPeriodId' in league_data:
            return league_data['scoringPeriodId']
    return 1


def get_team_roster(data, team_id):
    """Extract roster for a specific team with NFL team and positional ranking"""
    if not data:
        return []

    draft_detail = data.get('draftDetail', {})
    teams_data = draft_detail.get('teams', [])

    if not teams_data:
        teams_data = data.get('teams', [])

    for team in teams_data:
        if team.get('id') == team_id:
            roster_entries = team.get('roster', {}).get('entries', [])
            players = []

            for entry in roster_entries:
                player_pool_entry = entry.get('playerPoolEntry', {})
                player_info = player_pool_entry.get('player', {})
                player_name = player_info.get('fullName', 'Unknown')
                lineup_slot_id = entry.get('lineupSlotId', 0)
                pro_team_id = player_info.get('proTeamId')
                nfl_team = NFL_TEAMS.get(pro_team_id, 'N/A') if pro_team_id else 'N/A'
                nfl_logo = get_nfl_logo(nfl_team) if nfl_team != 'N/A' else ''
                ratings = player_pool_entry.get("ratings", {})
                positional_rank = ratings.get("0", {}).get("positionalRanking")

                if lineup_slot_id == 0:
                    position = 'QB'
                    sort_order = 1
                elif lineup_slot_id == 17:
                    position = 'K'
                    sort_order = 2
                elif lineup_slot_id == 18:
                    position = 'P'
                    sort_order = 3
                else:
                    position = f'SLOT-{lineup_slot_id}'
                    sort_order = 99

                players.append({
                    'Player': player_name,
                    'Position': position,
                    'NFL Team': nfl_team,
                    'NFL Logo': nfl_logo,
                    'Rank': positional_rank if positional_rank else '-',
                    'Sort': sort_order
                })

            players.sort(key=lambda x: x['Sort'])
            return players

    return []


def get_all_teams():
    """Get all teams from all leagues"""
    all_teams = []
    for league_name, league_id in LEAGUES.items():
        league_data = fetch_league_data(league_id)
        if league_data and 'teams' in league_data:
            for team in league_data['teams']:
                all_teams.append({
                    'league_name': league_name,
                    'league_id': league_id,
                    'team_id': team.get('id'),
                    'team_name': team.get('name', 'Unknown'),
                    'wins': team.get('record', {}).get('overall', {}).get('wins', 0),
                    'losses': team.get('record', {}).get('overall', {}).get('losses', 0)
                })
    return sorted(all_teams, key=lambda x: (x['league_name'], -x['wins']))


def process_league_standings(data, league_name):
    """Process league data into standings records"""
    if not data or 'teams' not in data:
        return []
    teams_data = []
    for team in data['teams']:
        # Get streak information
        record = team.get('record', {}).get('overall', {})
        streak_type = record.get('streakType', '')
        streak_length = record.get('streakLength', 0)

        # Format streak
        if streak_type and streak_length > 0:
            streak = f"{streak_type[0].upper()}{streak_length}"
        else:
            streak = "-"

        team_info = {
            'League': league_name,
            'Name': team.get('name', 'Unknown'),
            'Wins': team.get('record', {}).get('overall', {}).get('wins', 0),
            'Losses': team.get('record', {}).get('overall', {}).get('losses', 0),
            'Points For': team.get('record', {}).get('overall', {}).get('pointsFor', 0),
            'Points Against': team.get('record', {}).get('overall', {}).get('pointsAgainst', 0),
            'Transactions': team.get('transactionCounter', {}).get('acquisitions', 0),
            'Streak': streak
        }
        teams_data.append(team_info)
    return teams_data


def process_matchups(data, league_name):
    """Process matchup data for current week"""
    if not data or 'schedule' not in data:
        return []
    schedule = data.get('schedule', [])
    teams = data.get('teams', [])
    current_week = data.get('scoringPeriodId', 1)
    team_map = {team.get('id'): team.get('name', 'Unknown') for team in teams}
    logo_map = {team.get('id'): team.get('logo', '') for team in teams}

    matchups = []
    for matchup in schedule:
        matchup_week = matchup.get('matchupPeriodId')
        home = matchup.get('home', {})
        away = matchup.get('away', {})
        if not away:
            continue

        home_team_id = home.get('teamId')
        away_team_id = away.get('teamId')

        if matchup_week == current_week:
            home_score = round(home.get('totalPointsLive', 0), 1)
            away_score = round(away.get('totalPointsLive', 0), 1)
        else:
            home_score = round(home.get('totalPoints', 0), 1)
            away_score = round(away.get('totalPoints', 0), 1)

        matchup_info = {
            'League': league_name,
            'Week': matchup_week,
            'Home Team': team_map.get(home_team_id, 'Unknown'),
            'Home Logo': logo_map.get(home_team_id, ''),
            'Home Score': home_score,
            'Away Team': team_map.get(away_team_id, 'Unknown'),
            'Away Logo': logo_map.get(away_team_id, ''),
            'Away Score': away_score
        }
        matchups.append(matchup_info)
    return matchups


def fetch_all_matchups():
    """Fetch and aggregate matchups from all leagues"""
    all_matchups = []
    for league_name, league_id in LEAGUES.items():
        league_data = fetch_league_data(league_id)
        if league_data:
            matchups = process_matchups(league_data, league_name)
            all_matchups.extend(matchups)
    if not all_matchups:
        return None
    return pd.DataFrame(all_matchups)


def fetch_all_leagues():
    """Fetch and aggregate data from all leagues"""
    all_teams = []
    for league_name, league_id in LEAGUES.items():
        with st.spinner(f"Loading {league_name} league data..."):
            league_data = fetch_league_data(league_id)
            if league_data:
                teams = process_league_standings(league_data, league_name)
                all_teams.extend(teams)
    if not all_teams:
        return None
    df = pd.DataFrame(all_teams)
    df = df.sort_values(by=['Wins', 'Points For'], ascending=[False, False])
    df.insert(0, 'Rank', range(1, len(df) + 1))
    df['Points For'] = df['Points For'].round(1)
    df['Points Against'] = df['Points Against'].round(1)
    return df


def calculate_playoff_standings(df, matchups_df=None):
    """Calculate playoff standings with league winner guarantee and min 2 per league rule"""
    if df is None or df.empty:
        return None

    all_teams = df.copy()

    # Apply weekly high score bonus
    if matchups_df is not None and not matchups_df.empty:
        all_performances = []
        for _, matchup in matchups_df.iterrows():
            if matchup['Home Score'] > 0:
                all_performances.append({
                    'Team': matchup['Home Team'],
                    'League': matchup['League'],
                    'Score': matchup['Home Score']
                })
            if matchup['Away Score'] > 0:
                all_performances.append({
                    'Team': matchup['Away Team'],
                    'League': matchup['League'],
                    'Score': matchup['Away Score']
                })

        if all_performances:
            highest_performance = max(all_performances, key=lambda x: x['Score'])
            bonus_team = highest_performance['Team']
            bonus_league = highest_performance['League']
            mask = (all_teams['Name'] == bonus_team) & (all_teams['League'] == bonus_league)
            all_teams.loc[mask, 'Wins'] = all_teams.loc[mask, 'Wins'] + 0.5

    # Sort all teams by wins and points
    all_teams = all_teams.sort_values(by=['Wins', 'Points For'], ascending=[False, False]).reset_index(drop=True)

    # Step 1: Identify league winners (top team from each league)
    league_winners = {}
    for league_name in LEAGUES.keys():
        league_teams = all_teams[all_teams['League'] == league_name]
        if not league_teams.empty:
            league_winners[league_name] = league_teams.iloc[0]['Name']

    # Step 2: Add all league winners first
    playoff_teams = []
    league_counts = {league: 0 for league in LEAGUES.keys()}

    for _, team in all_teams.iterrows():
        if team['Name'] in league_winners.values():
            playoff_teams.append(team.to_dict())
            league_counts[team['League']] += 1

    # Step 3: Ensure minimum 2 teams per league
    for league_name in LEAGUES.keys():
        if league_counts[league_name] < 2:
            # Find the next best team from this league that's not already in playoffs
            league_teams = all_teams[all_teams['League'] == league_name]
            for _, team in league_teams.iterrows():
                # Check if team is already in playoffs
                if any(p['Name'] == team['Name'] and p['League'] == team['League'] for p in playoff_teams):
                    continue
                # Add this team
                playoff_teams.append(team.to_dict())
                league_counts[league_name] += 1
                if league_counts[league_name] >= 2:
                    break

    # Step 4: Fill remaining spots with best available teams (up to 8 total)
    for _, team in all_teams.iterrows():
        if len(playoff_teams) >= 8:
            break
        # Check if team is already in playoffs
        if any(p['Name'] == team['Name'] and p['League'] == team['League'] for p in playoff_teams):
            continue
        # Add team
        playoff_teams.append(team.to_dict())
        league_counts[team['League']] += 1

    # Create result dataframe with all teams
    result_teams = []
    for _, team in all_teams.iterrows():
        team_dict = team.to_dict()
        result_teams.append(team_dict)

    result_df = pd.DataFrame(result_teams)
    result_df['Rank'] = range(1, len(result_df) + 1)
    result_df = result_df[['Rank', 'Name', 'League', 'Wins', 'Points For', 'Points Against', 'Streak']]
    return result_df
