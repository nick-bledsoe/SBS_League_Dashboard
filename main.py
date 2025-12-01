import streamlit as st
import requests
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="SBS League Dash",
    page_icon="coachSmith.png",
    layout="wide"
)

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


def get_team_roster(data, team_id):
    """Extract roster for a specific team with NFL team and positional ranking"""
    if not data:
        return []

    # Try to get from draftDetail first (has more complete data)
    draft_detail = data.get('draftDetail', {})
    teams_data = draft_detail.get('teams', [])

    # If draftDetail not available, fall back to regular teams data
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

                # Get lineupSlotId from the entry
                lineup_slot_id = entry.get('lineupSlotId', 0)

                # Get NFL team
                pro_team_id = player_info.get('proTeamId')
                nfl_team = NFL_TEAMS.get(pro_team_id, 'N/A') if pro_team_id else 'N/A'

                # Get positional ranking
                ratings = player_pool_entry.get("ratings", {})
                positional_rank = ratings.get("0", {}).get("positionalRanking")

                # Map lineup slot to position types
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
        team_info = {
            'League': league_name,
            'Name': team.get('name', 'Unknown'),
            'Wins': team.get('record', {}).get('overall', {}).get('wins', 0),
            'Losses': team.get('record', {}).get('overall', {}).get('losses', 0),
            'Points For': team.get('record', {}).get('overall', {}).get('pointsFor', 0),
            'Points Against': team.get('record', {}).get('overall', {}).get('pointsAgainst', 0),
            'Transactions': team.get('transactionCounter', {}).get('acquisitions', 0)
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

    # Create team ID to name mapping
    team_map = {team.get('id'): team.get('name', 'Unknown') for team in teams}

    matchups = []
    for matchup in schedule:
        matchup_week = matchup.get('matchupPeriodId')

        home = matchup.get('home', {})
        away = matchup.get('away', {})

        # Skip if no away team (bye week)
        if not away:
            continue

        home_team_id = home.get('teamId')
        away_team_id = away.get('teamId')

        # Get scores - use totalPointsLive for current week, totalPoints for completed weeks
        if matchup_week == current_week:
            # For current/live week, use totalPointsLive
            home_score = round(home.get('totalPointsLive', 0), 1)
            away_score = round(away.get('totalPointsLive', 0), 1)
        else:
            # For completed weeks, use totalPoints
            home_score = round(home.get('totalPoints', 0), 1)
            away_score = round(away.get('totalPoints', 0), 1)

        matchup_info = {
            'League': league_name,
            'Week': matchup_week,
            'Home Team': team_map.get(home_team_id, 'Unknown'),
            'Home Score': home_score,
            'Away Team': team_map.get(away_team_id, 'Unknown'),
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

    # Create DataFrame
    df = pd.DataFrame(all_matchups)

    return df


def get_current_week():
    """Get current scoring period from any league"""
    for league_id in LEAGUES.values():
        league_data = fetch_league_data(league_id)
        if league_data and 'scoringPeriodId' in league_data:
            return league_data['scoringPeriodId']
    return 1


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

    # Create DataFrame
    df = pd.DataFrame(all_teams)

    # Sort by Wins (descending), then by Points For (descending)
    df = df.sort_values(by=['Wins', 'Points For'], ascending=[False, False])

    # Add Rank column
    df.insert(0, 'Rank', range(1, len(df) + 1))

    # Round points to 1 decimal place
    df['Points For'] = df['Points For'].round(1)
    df['Points Against'] = df['Points Against'].round(1)

    return df


def calculate_playoff_standings(df, matchups_df=None):
    """Calculate playoff standings with league winner guarantee and max 3 per league rule"""
    if df is None or df.empty:
        return None

    # Create a copy and ensure it's sorted by Wins then Points For
    all_teams = df.copy()

    # Add 0.5 win bonus for highest single week score of the season
    if matchups_df is not None and not matchups_df.empty:
        # Get all team performances across all weeks
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

        # Find the highest single week score
        if all_performances:
            highest_performance = max(all_performances, key=lambda x: x['Score'])
            bonus_team = highest_performance['Team']
            bonus_league = highest_performance['League']

            # Add 0.5 wins to that team
            mask = (all_teams['Name'] == bonus_team) & (all_teams['League'] == bonus_league)
            all_teams.loc[mask, 'Wins'] = all_teams.loc[mask, 'Wins'] + 0.5

    all_teams = all_teams.sort_values(by=['Wins', 'Points For'], ascending=[False, False]).reset_index(drop=True)

    # Step 1: Identify the top team from each league (automatic qualifiers)
    league_winners = {}
    for league_name in LEAGUES.keys():
        league_teams = all_teams[all_teams['League'] == league_name]
        if not league_teams.empty:
            league_winners[league_name] = league_teams.iloc[0]['Name']

    # Step 2: Build playoff list
    playoff_teams = []
    league_counts = {league: 0 for league in LEAGUES.keys()}

    # First pass: Add league winners
    for _, team in all_teams.iterrows():
        if team['Name'] in league_winners.values():
            playoff_teams.append(team.to_dict())
            league_counts[team['League']] += 1

    # Second pass: Fill remaining spots (up to 8 total, max 3 per league)
    for _, team in all_teams.iterrows():
        if len(playoff_teams) >= 8:
            break

        # Skip if already in playoffs
        if any(p['Name'] == team['Name'] and p['League'] == team['League'] for p in playoff_teams):
            continue

        # Add if league has room
        if league_counts[team['League']] < 3:
            playoff_teams.append(team.to_dict())
            league_counts[team['League']] += 1

    # Step 3: Build result with all teams
    playoff_team_keys = {(t['Name'], t['League']) for t in playoff_teams}

    result_teams = []
    for _, team in all_teams.iterrows():
        team_dict = team.to_dict()
        result_teams.append(team_dict)

    # Create final dataframe with proper ranking
    result_df = pd.DataFrame(result_teams)
    result_df['Rank'] = range(1, len(result_df) + 1)

    # Reorder columns
    result_df = result_df[['Rank', 'Name', 'League', 'Wins', 'Points For', 'Points Against']]

    return result_df


# Initialize session state for tab
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'Standings'

# Header
col1, col2 = st.columns([10, 1])

with col1:
    st.title("_SBS League Dashboard_")
    st.subheader(":orange[2025 quest for the Coach Smith Cup]")

with col2:
    st.image("coachSmith.png", width=53)

# Navigation tabs
tab1, tab2 = st.tabs(["Home", "Teams"], default="Home")

# HOME TAB
with tab1:
    st.markdown("")

    # Fetch and display data
    if st.button("Refresh Data", key="refresh_standings"):
        st.rerun()

    standings_df = fetch_all_leagues()

    if standings_df is not None:
        # Playoff Picture
        st.subheader("🏆 Playoff Standings")
        st.caption(
            "Top team from each league automatically qualifies | Max 3 teams per league | +0.5 win bonus for highest single week score.")

        matchups_df = fetch_all_matchups()
        playoff_df = calculate_playoff_standings(standings_df, matchups_df)

        if playoff_df is not None:
            # Calculate games back from playoff cutoff (8th seed)
            eighth_seed_wins = playoff_df.iloc[7]['Wins'] if len(playoff_df) >= 8 else 0
            playoff_df['GB'] = playoff_df['Wins'] - eighth_seed_wins

            # Reorder columns to put GB between Wins and Points For
            playoff_df = playoff_df[['Rank', 'Name', 'League', 'Wins', 'GB', 'Points For', 'Points Against']]


            # Color code the seed column
            def color_seed(val):
                if val <= 8:
                    return 'background-color: #007309'
                elif val <= 18:
                    return 'background-color: #910016'
                return ''


            st.dataframe(
                playoff_df.head(18).style.applymap(color_seed, subset=['Rank']),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn(
                        "Seed",
                        width="small"
                    ),
                    "Name": st.column_config.TextColumn(
                        "Team Name",
                        width="medium"
                    ),
                    "League": st.column_config.TextColumn(
                        "Divison",
                        width="small"
                    ),
                    "Wins": st.column_config.NumberColumn(
                        "W",
                        width="small",
                        format="%.1f"
                    ),
                    "GB": st.column_config.NumberColumn(
                        "GB",
                        width="small",
                        format="%.1f",
                        help="Games back from playoff cutoff (8th seed)"
                    ),
                    "Points For": st.column_config.NumberColumn(
                        "PF",
                        format="%.1f"
                    ),
                    "Points Against": st.column_config.NumberColumn(
                        "PA",
                        format="%.1f"
                    )
                }
            )

            # Playoff summary
            playoff_teams = playoff_df.head(8)
            league_counts = playoff_teams['League'].value_counts()

            col1, col2, col3 = st.columns(3)
            for idx, league_name in enumerate(LEAGUES.keys()):
                with [col1, col2, col3][idx]:
                    count = league_counts.get(league_name, 0)
                    st.metric(f"{league_name} Teams", f"{count}")

        # League breakdown
        st.markdown("---")
        st.subheader("Division Breakdown")

        col1, col2, col3 = st.columns(3)

        for idx, (league_name, col) in enumerate(zip(LEAGUES.keys(), [col1, col2, col3])):
            with col:
                league_df = standings_df[standings_df['League'] == league_name].copy()
                league_df['Rank'] = range(1, len(league_df) + 1)
                st.write(f":orange[**{league_name}**]")
                st.dataframe(
                    league_df[['Rank', 'Name', 'Wins', 'Losses', 'Points For', 'Transactions']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Points For": st.column_config.NumberColumn(
                            "Points For",
                            format="%.1f"
                        )
                    }
                )

        # Weekly High Scores
        st.markdown("---")
        st.subheader("Weekly High Scores")
        st.caption("Highest scoring team each week across all divisions")

        if matchups_df is None:
            matchups_df = fetch_all_matchups()

        if matchups_df is not None and not matchups_df.empty:
            weekly_high_scores = []

            for week in sorted(matchups_df['Week'].unique()):
                week_data = matchups_df[matchups_df['Week'] == week]

                # Get all team performances for the week
                performances = []
                for _, matchup in week_data.iterrows():
                    # Only include if scores are greater than 0 (week has been played)
                    if matchup['Home Score'] > 0 or matchup['Away Score'] > 0:
                        performances.append({
                            'Week': week,
                            'Team Name': matchup['Home Team'],
                            'League': matchup['League'],
                            'Score': matchup['Home Score'],
                            'Opponent': matchup['Away Team']
                        })
                        performances.append({
                            'Week': week,
                            'Team Name': matchup['Away Team'],
                            'League': matchup['League'],
                            'Score': matchup['Away Score'],
                            'Opponent': matchup['Home Team']
                        })

                # Find highest score for the week
                if performances:
                    highest = max(performances, key=lambda x: x['Score'])
                    weekly_high_scores.append(highest)

            if weekly_high_scores:
                high_scores_df = pd.DataFrame(weekly_high_scores)
                high_scores_df = high_scores_df.sort_values('Week', ascending=False)

                st.dataframe(
                    high_scores_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Week": st.column_config.NumberColumn(
                            "Week",
                            width="small"
                        ),
                        "Team Name": st.column_config.TextColumn(
                            "Team",
                            width="medium"
                        ),
                        "League": st.column_config.TextColumn(
                            "Division",
                            width="small"
                        ),
                        "Score": st.column_config.NumberColumn(
                            "Score",
                            format="%.1f",
                            width="small"
                        ),
                        "Opponent": st.column_config.TextColumn(
                            "Opponent",
                            width="medium"
                        )
                    }
                )

                # Summary stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    highest_overall = high_scores_df.loc[high_scores_df['Score'].idxmax()]
                    st.metric("Highest Score", f"{highest_overall['Score']:.1f}",
                              f"{highest_overall['Team Name']} (Week {highest_overall['Week']})")
                with col2:
                    avg_high_score = high_scores_df['Score'].mean()
                    st.metric("Average Weekly High", f"{avg_high_score:.1f}")
                with col3:
                    # Count weekly highs by league
                    league_highs = high_scores_df['League'].value_counts()
                    most_highs_league = league_highs.idxmax() if not league_highs.empty else "N/A"
                    st.metric("Most Weekly Highs", most_highs_league, f"{league_highs.max()} weeks")
        else:
            st.info("No matchup data available for weekly high scores")

        # Matchups Section
        st.markdown("---")
        st.subheader("Matchups")

        if matchups_df is not None and not matchups_df.empty:
            current_week = get_current_week()

            # Get all available weeks
            available_weeks = sorted(matchups_df['Week'].unique())

            # Create week options with current week indicator
            week_options = [f"{week} (current week)" if week == current_week else str(week) for week in available_weeks]

            # Week selector
            selected_week_display = st.selectbox(
                ":grey[Select Week]",
                options=week_options,
                index=available_weeks.index(current_week) if current_week in available_weeks else 0,
                key="week_selector"
            )

            # Extract the actual week number from the selection
            selected_week = int(selected_week_display.split()[0])

            # Filter matchups for selected week
            week_matchups = matchups_df[matchups_df['Week'] == selected_week]

            # Display matchups grouped by league in columns
            cols = st.columns(3)

            for idx, league_name in enumerate(LEAGUES.keys()):
                with cols[idx]:
                    league_matchups = week_matchups[week_matchups['League'] == league_name]

                    # League header with styling
                    st.markdown(f"### :orange[{league_name}]")

                    if not league_matchups.empty:
                        # Get team info for this league
                        league_teams = playoff_df[
                            playoff_df['League'] == league_name] if playoff_df is not None else None

                        # Display each matchup
                        for _, matchup in league_matchups.iterrows():
                            # Determine winner for highlighting
                            home_winning = matchup['Home Score'] > matchup['Away Score']
                            away_winning = matchup['Away Score'] > matchup['Home Score']

                            # Get team records and seeds
                            home_team_info = league_teams[league_teams['Name'] == matchup['Home Team']].iloc[
                                0] if league_teams is not None and not league_teams[
                                league_teams['Name'] == matchup['Home Team']].empty else None
                            away_team_info = league_teams[league_teams['Name'] == matchup['Away Team']].iloc[
                                0] if league_teams is not None and not league_teams[
                                league_teams['Name'] == matchup['Away Team']].empty else None

                            home_record = f"({int(home_team_info['Wins'])}-{standings_df[(standings_df['Name'] == matchup['Home Team']) & (standings_df['League'] == league_name)].iloc[0]['Losses']}, {home_team_info['Rank']}{'st' if home_team_info['Rank'] == 1 else 'nd' if home_team_info['Rank'] == 2 else 'rd' if home_team_info['Rank'] == 3 else 'th'})" if home_team_info is not None else ""
                            away_record = f"({int(away_team_info['Wins'])}-{standings_df[(standings_df['Name'] == matchup['Away Team']) & (standings_df['League'] == league_name)].iloc[0]['Losses']}, {away_team_info['Rank']}{'st' if away_team_info['Rank'] == 1 else 'nd' if away_team_info['Rank'] == 2 else 'rd' if away_team_info['Rank'] == 3 else 'th'})" if away_team_info is not None else ""

                            # Create matchup card
                            with st.container(border=True):
                                # Home team row
                                st.markdown(f"""
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                        <div>
                                            <div style="{'font-weight: bold;' if home_winning else ''} font-size: 16px;">{matchup['Home Team']}</div>
                                            <div style="font-size: 12px; color: #666; margin-top: 2px;">{home_record}</div>
                                        </div>
                                        <div style="font-size: 24px; font-weight: bold; color: {'#3eab43' if home_winning else '#666'};">{matchup['Home Score']:.1f}</div>
                                    </div>
                                """, unsafe_allow_html=True)

                                # Away team row
                                st.markdown(f"""
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>
                                            <div style="{'font-weight: bold;' if away_winning else ''} font-size: 16px;">{matchup['Away Team']}</div>
                                            <div style="font-size: 12px; color: #666; margin-top: 2px; margin-bottom: 8px;">{away_record}</div>
                                        </div>
                                        <div style="font-size: 24px; font-weight: bold; color: {'#3eab43' if away_winning else '#666'};">{matchup['Away Score']:.1f}</div>
                                    </div>
                                """, unsafe_allow_html=True)

                    else:
                        st.info(f"No matchups for week {selected_week}")

                    st.write("")  # Add spacing
        else:
            st.info("No matchups available")
    else:
        st.error("Failed to fetch league data")

# TEAMS TAB
with tab2:
    st.markdown("")

    # Get all teams
    all_teams = get_all_teams()

    if all_teams:
        # Create team selection options
        team_options = [f"{team['team_name']} ({team['league_name']})"
                        for team in all_teams]

        # Team selector
        selected_team_display = st.selectbox(
            ":grey[Select a team to view roster]",
            options=team_options,
            key="team_selector"
        )

        # Find the selected team
        selected_idx = team_options.index(selected_team_display)
        selected_team = all_teams[selected_idx]

        # Fetch roster data
        league_data = fetch_league_data(selected_team['league_id'])

        if league_data:
            roster = get_team_roster(league_data, selected_team['team_id'])

            # Get team's seed from playoff standings
            standings_df = fetch_all_leagues()
            matchups_df = fetch_all_matchups()
            playoff_df = calculate_playoff_standings(standings_df, matchups_df)

            team_seed = "N/A"
            if playoff_df is not None:
                team_row = playoff_df[(playoff_df['Name'] == selected_team['team_name']) &
                                      (playoff_df['League'] == selected_team['league_name'])]
                if not team_row.empty:
                    team_seed = int(team_row.iloc[0]['Rank'])

            # Display team info header
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.metric(":grey[Team]", f"{selected_team['team_name']}")
            with col2:
                st.metric(":grey[Division]", selected_team['league_name'])
            with col3:
                st.metric(":grey[Record]", f"{selected_team['wins']}-{selected_team['losses']}")
            with col4:
                st.metric(":grey[Seed]", f"{team_seed}{'st' if team_seed == 1 else 'nd' if team_seed == 2 else 'rd' if team_seed == 3 else 'th'}")

            st.markdown("---")

            if roster:
                # Separate by position
                qbs = [p for p in roster if p['Position'] == 'QB']
                kickers = [p for p in roster if p['Position'] == 'K']
                punters = [p for p in roster if p['Position'] == 'P']

                # Display in columns
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.subheader(":orange[Quarterback]")
                    if qbs:
                        qb_df = pd.DataFrame(qbs)
                        st.dataframe(
                            qb_df[['Player', 'NFL Team', 'Rank']],
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Player": st.column_config.TextColumn("Player", width="medium"),
                                "NFL Team": st.column_config.TextColumn("Team", width="small"),
                                "Rank": st.column_config.TextColumn("Pos Rank", width="small")
                            }
                        )
                    else:
                        st.info("No QBs")

                with col2:
                    st.subheader(":orange[Kickers]")
                    if kickers:
                        k_df = pd.DataFrame(kickers)
                        st.dataframe(
                            k_df[['Player', 'NFL Team', 'Rank']],
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Player": st.column_config.TextColumn("Player", width="medium"),
                                "NFL Team": st.column_config.TextColumn("Team", width="small"),
                                "Rank": st.column_config.TextColumn("Pos Rank", width="small")
                            }
                        )
                    else:
                        st.info("No Kickers")

                with col3:
                    st.subheader(":orange[Punters]")
                    if punters:
                        p_df = pd.DataFrame(punters)
                        st.dataframe(
                            p_df[['Player', 'NFL Team', 'Rank']],
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Player": st.column_config.TextColumn("Player", width="medium"),
                                "NFL Team": st.column_config.TextColumn("Team", width="small"),
                                "Rank": st.column_config.TextColumn("Pos Rank", width="small")
                            }
                        )
                    else:
                        st.info("No Punters")
            else:
                st.warning("No roster data available for this team")
        else:
            st.error("Failed to fetch roster data")
    else:
        st.error("Failed to load teams")

# Add footer
st.caption("_Data sourced from ESPN Fantasy Football API - Created by Nick Bledsoe (2025)_")