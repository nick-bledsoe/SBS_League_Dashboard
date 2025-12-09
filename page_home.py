from utils import *
import json
import os

MATCHUPS_FILE = "playoff_matchups.json"


def load_playoff_matchups():
    """Load playoff matchups from JSON file"""
    if os.path.exists(MATCHUPS_FILE):
        try:
            with open(MATCHUPS_FILE, 'r') as f:
                data = json.load(f)
                # Convert string keys back to integers
                return {int(k): v for k, v in data.items()}
        except Exception as e:
            return {}
    return {}


def get_team_score_for_week(league_id, team_name, week):
    """Get a specific team's score for a specific week"""
    league_data = fetch_league_data(league_id)
    if not league_data or 'schedule' not in league_data:
        return None

    schedule = league_data.get('schedule', [])
    teams = league_data.get('teams', [])
    team_map = {team.get('id'): team.get('name', 'Unknown') for team in teams}

    for matchup in schedule:
        if matchup.get('matchupPeriodId') == week:
            home = matchup.get('home', {})
            away = matchup.get('away', {})

            home_team_id = home.get('teamId')
            away_team_id = away.get('teamId')
            home_team_name = team_map.get(home_team_id)
            away_team_name = team_map.get(away_team_id)

            current_week = league_data.get('scoringPeriodId', 1)

            if home_team_name == team_name:
                if week == current_week:
                    return round(home.get('totalPointsLive', 0), 1)
                else:
                    return round(home.get('totalPoints', 0), 1)
            elif away_team_name == team_name:
                if week == current_week:
                    return round(away.get('totalPointsLive', 0), 1)
                else:
                    return round(away.get('totalPoints', 0), 1)

    return None


def render_home_tab():
    st.markdown("")

    if st.button("Refresh Data", key="refresh_standings"):
        st.rerun()

    standings_df = fetch_all_leagues()

    if standings_df is not None:
        # Playoff Picture
        st.subheader("🏆 Standings")
        st.caption(
            "Top team from each div automatically qualifies | Min 2 teams per div | +0.5 win bonus for highest single week score.")

        matchups_df = fetch_all_matchups()
        playoff_df = calculate_playoff_standings(standings_df, matchups_df)

        if playoff_df is not None:
            eighth_seed_wins = playoff_df.iloc[7]['Wins'] if len(playoff_df) >= 8 else 0
            playoff_df['GB'] = playoff_df['Wins'] - eighth_seed_wins
            playoff_df['Team Display'] = playoff_df['Name'].apply(
                lambda x: f"{x} ({TEAM_OWNERS.get(x, '')})" if TEAM_OWNERS.get(x) else x)
            playoff_df_display = playoff_df[
                ['Rank', 'Team Display', 'League', 'Wins', 'GB', 'Points For', 'Streak']].copy()

            def color_seed(val):
                if val <= 8:
                    return 'background-color: #007309'
                elif val <= 18:
                    return 'background-color: #910016'
                return ''

            st.dataframe(
                playoff_df_display.head(18).style.applymap(color_seed, subset=['Rank']),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn("Seed", width="small"),
                    "Team Display": st.column_config.TextColumn("Team", width="medium"),
                    "League": st.column_config.TextColumn("Division", width="small"),
                    "Wins": st.column_config.NumberColumn("W", width="small", format="%.1f"),
                    "GB": st.column_config.NumberColumn("GB", width="small", format="%.1f",
                                                        help="Games back from playoff cutoff (8th seed)"),
                    "Points For": st.column_config.NumberColumn("PF", format="%.1f"),
                    "Streak": st.column_config.TextColumn("Streak", width="small")
                }
            )

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
                league_df['Team Display'] = league_df['Name'].apply(
                    lambda x: f"{x} ({TEAM_OWNERS.get(x, '')})" if TEAM_OWNERS.get(x) else x)
                league_df['Record'] = league_df['Wins'].astype(int).astype(str) + "-" + league_df['Losses'].astype(
                    int).astype(str)

                st.markdown(f"### :orange[{league_name}]")
                st.dataframe(
                    league_df[['Rank', 'Team Display', 'Record', 'Points For', 'Points Against', 'Transactions']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Rank": st.column_config.NumberColumn("Rank", width="small"),
                        "Team Display": st.column_config.TextColumn("Team", width="medium"),
                        "Record": st.column_config.TextColumn("Record", width="small"),
                        "Points For": st.column_config.NumberColumn("PF", format="%.1f"),
                        "Points Against": st.column_config.NumberColumn("PA", format="%.1f"),
                        "Transactions": st.column_config.NumberColumn("Moves", width="small")
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

                performances = []
                for _, matchup in week_data.iterrows():
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

                if performances:
                    highest = max(performances, key=lambda x: x['Score'])
                    weekly_high_scores.append(highest)

            if weekly_high_scores:
                high_scores_df = pd.DataFrame(weekly_high_scores)
                high_scores_df = high_scores_df.sort_values('Week', ascending=False)

                # Add owner names to team display and opponent display
                high_scores_df['Team Display'] = high_scores_df['Team Name'].apply(
                    lambda x: f"{x} ({TEAM_OWNERS.get(x, '')})" if TEAM_OWNERS.get(x) else x
                )
                high_scores_df['Opponent Display'] = high_scores_df['Opponent'].apply(
                    lambda x: f"{x} ({TEAM_OWNERS.get(x, '')})" if TEAM_OWNERS.get(x) else x
                )

                st.dataframe(
                    high_scores_df[['Week', 'Team Display', 'League', 'Score', 'Opponent Display']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Week": st.column_config.NumberColumn("Week", width="small"),
                        "Team Display": st.column_config.TextColumn("Team", width="medium"),
                        "League": st.column_config.TextColumn("Division", width="small"),
                        "Score": st.column_config.NumberColumn("Score", format="%.1f", width="small"),
                        "Opponent Display": st.column_config.TextColumn("Opponent", width="medium")
                    }
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    highest_overall = high_scores_df.loc[high_scores_df['Score'].idxmax()]
                    team_with_owner = f"{highest_overall['Team Name']} ({TEAM_OWNERS.get(highest_overall['Team Name'], '')})" if TEAM_OWNERS.get(
                        highest_overall['Team Name']) else highest_overall['Team Name']
                    st.metric("Highest Score", f"{highest_overall['Score']:.1f}",
                              f"{team_with_owner} - Week {highest_overall['Week']}")
                with col2:
                    avg_high_score = high_scores_df['Score'].mean()
                    st.metric("Average Weekly High", f"{avg_high_score:.1f}")
                with col3:
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

            # Load playoff matchups
            playoff_matchups = load_playoff_matchups()

            # Determine if we have playoff matchups for current week
            has_playoff_matchups = bool(
                playoff_matchups and current_week in playoff_matchups and playoff_matchups[current_week])

            # Default to playoff matchups if week 16+ and they exist, otherwise regular season
            default_matchup_type = "Playoffs" if (current_week >= 16 and has_playoff_matchups) else "Regular Season"

            # Matchup type selector
            col1, col2 = st.columns([2, 6])
            with col1:
                matchup_type = st.selectbox(
                    ":grey[Matchup Type]",
                    options=["Regular Season", "Playoffs"],
                    index=0 if default_matchup_type == "Regular Season" else 1,
                    key="matchup_type_selector"
                )

            with col2:
                if matchup_type == "Regular Season":
                    available_weeks = sorted(matchups_df['Week'].unique())
                    week_options = [f"{week} (current week)" if week == current_week else str(week) for week in
                                    available_weeks]

                    selected_week_display = st.selectbox(
                        ":grey[Select Week]",
                        options=week_options,
                        index=available_weeks.index(current_week) if current_week in available_weeks else 0,
                        key="week_selector"
                    )
                    selected_week = int(selected_week_display.split()[0])
                else:
                    # For playoff matchups, show weeks that have playoff matchups
                    playoff_weeks = sorted([week for week, matchups in playoff_matchups.items() if matchups])
                    if playoff_weeks:
                        playoff_week_options = [f"{week} (current week)" if week == current_week else str(week) for week
                                                in playoff_weeks]
                        selected_week_display = st.selectbox(
                            ":grey[Select Week]",
                            options=playoff_week_options,
                            index=playoff_weeks.index(current_week) if current_week in playoff_weeks else len(
                                playoff_weeks) - 1,
                            key="home_playoff_week_selector"
                        )
                        selected_week = int(selected_week_display.split()[0])
                    else:
                        st.info("No playoff matchups created yet. Go to the Playoffs tab to create matchups.")
                        return

            st.markdown("")

            if matchup_type == "Regular Season":
                # Display regular season matchups (existing code)
                week_matchups = matchups_df[matchups_df['Week'] == selected_week]

                cols = st.columns(3)

                for idx, league_name in enumerate(LEAGUES.keys()):
                    with cols[idx]:
                        league_matchups = week_matchups[week_matchups['League'] == league_name]
                        st.markdown(f"### :orange[{league_name}]")

                        if not league_matchups.empty:
                            league_teams = playoff_df[
                                playoff_df['League'] == league_name] if playoff_df is not None else None

                            for _, matchup in league_matchups.iterrows():
                                home_winning = matchup['Home Score'] > matchup['Away Score']
                                away_winning = matchup['Away Score'] > matchup['Home Score']

                                home_team_info = league_teams[league_teams['Name'] == matchup['Home Team']].iloc[
                                    0] if league_teams is not None and not league_teams[
                                    league_teams['Name'] == matchup['Home Team']].empty else None
                                away_team_info = league_teams[league_teams['Name'] == matchup['Away Team']].iloc[
                                    0] if league_teams is not None and not league_teams[
                                    league_teams['Name'] == matchup['Away Team']].empty else None

                                home_record = f"({int(home_team_info['Wins'])}-{standings_df[(standings_df['Name'] == matchup['Home Team']) & (standings_df['League'] == league_name)].iloc[0]['Losses']}, {home_team_info['Rank']}{'st' if home_team_info['Rank'] == 1 else 'nd' if home_team_info['Rank'] == 2 else 'rd' if home_team_info['Rank'] == 3 else 'th'})" if home_team_info is not None else ""
                                away_record = f"({int(away_team_info['Wins'])}-{standings_df[(standings_df['Name'] == matchup['Away Team']) & (standings_df['League'] == league_name)].iloc[0]['Losses']}, {away_team_info['Rank']}{'st' if away_team_info['Rank'] == 1 else 'nd' if away_team_info['Rank'] == 2 else 'rd' if away_team_info['Rank'] == 3 else 'th'})" if away_team_info is not None else ""

                                # Get owner names
                                home_owner = TEAM_OWNERS.get(matchup['Home Team'], "")
                                away_owner = TEAM_OWNERS.get(matchup['Away Team'], "")

                                with st.container(border=True):
                                    st.markdown(f"""
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                            <div style="display: flex; align-items: center; gap: 10px;">
                                                <img src="{matchup['Home Logo']}" style="width: 30px; height: 30px; border-radius: 50%;" onerror="this.style.display='none'">
                                                <div>
                                                    <div style="{'font-weight: bold;' if home_winning else ''} font-size: 16px;">
                                                        {matchup['Home Team']} <span style="font-size: 13px; color: #888; font-weight: normal; margin-left: 5px;">{home_owner}</span>
                                                    </div>
                                                    <div style="font-size: 12px; color: #666; margin-top: 2px;">{home_record}</div>
                                                </div>
                                            </div>
                                            <div style="font-size: 24px; font-weight: bold; color: {'#3eab43' if home_winning else '#666'};">{matchup['Home Score']:.1f}</div>
                                        </div>
                                    """, unsafe_allow_html=True)

                                    st.markdown(f"""
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <div style="display: flex; align-items: center; gap: 10px;">
                                                <img src="{matchup['Away Logo']}" style="width: 30px; height: 30px; border-radius: 50%;" onerror="this.style.display='none'">
                                                <div>
                                                    <div style="{'font-weight: bold;' if away_winning else ''} font-size: 16px;">
                                                        {matchup['Away Team']} <span style="font-size: 13px; color: #888; font-weight: normal; margin-left: 5px;">{away_owner}</span>
                                                    </div>
                                                    <div style="font-size: 12px; color: #666; margin-top: 2px; margin-bottom: 8px;">{away_record}</div>
                                                </div>
                                            </div>
                                            <div style="font-size: 24px; font-weight: bold; color: {'#3eab43' if away_winning else '#666'};">{matchup['Away Score']:.1f}</div>
                                        </div>
                                    """, unsafe_allow_html=True)

                        else:
                            st.info(f"No matchups for week {selected_week}")

                        st.write("")

            else:
                # Display playoff matchups
                week_playoff_matchups = playoff_matchups.get(selected_week, [])

                if not week_playoff_matchups:
                    st.info(f"No playoff matchups for week {selected_week}")
                else:
                    # Add playoff header
                    st.markdown("### :orange[Coach Smith Cup Playoffs]")
                    st.markdown("")

                    # Display playoff matchups across columns
                    num_matchups = len(week_playoff_matchups)
                    cols = st.columns(min(3, num_matchups))

                    for idx, matchup in enumerate(week_playoff_matchups):
                        with cols[idx % 3]:
                            team1 = matchup['team1']
                            team2 = matchup['team2']

                            # Get team logos
                            team1_logo = ""
                            team2_logo = ""

                            league1_data = fetch_league_data(team1['league_id'])
                            if league1_data and 'teams' in league1_data:
                                for team in league1_data['teams']:
                                    if team.get('id') == team1['team_id']:
                                        team1_logo = team.get('logo', '')
                                        break

                            league2_data = fetch_league_data(team2['league_id'])
                            if league2_data and 'teams' in league2_data:
                                for team in league2_data['teams']:
                                    if team.get('id') == team2['team_id']:
                                        team2_logo = team.get('logo', '')
                                        break

                            # Get seeds from playoff standings
                            team1_seed = "N/A"
                            team2_seed = "N/A"

                            if playoff_df is not None:
                                team1_row = playoff_df[(playoff_df['Name'] == team1['team_name']) &
                                                       (playoff_df['League'] == team1['league_name'])]
                                if not team1_row.empty:
                                    team1_seed = int(team1_row.iloc[0]['Rank'])

                                team2_row = playoff_df[(playoff_df['Name'] == team2['team_name']) &
                                                       (playoff_df['League'] == team2['league_name'])]
                                if not team2_row.empty:
                                    team2_seed = int(team2_row.iloc[0]['Rank'])

                            # Get scores for selected week
                            team1_score = get_team_score_for_week(team1['league_id'], team1['team_name'], selected_week)
                            team2_score = get_team_score_for_week(team2['league_id'], team2['team_name'], selected_week)

                            # Determine winner
                            team1_winning = False
                            team2_winning = False
                            if team1_score is not None and team2_score is not None:
                                if team1_score > team2_score:
                                    team1_winning = True
                                elif team2_score > team1_score:
                                    team2_winning = True

                            # Get owner names
                            team1_owner = TEAM_OWNERS.get(team1['team_name'], "")
                            team2_owner = TEAM_OWNERS.get(team2['team_name'], "")

                            with st.container(border=True):
                                # Team 1
                                st.markdown(f"""
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                        <div style="display: flex; align-items: center; gap: 10px;">
                                            <img src="{team1_logo}" style="width: 30px; height: 30px; border-radius: 50%;" onerror="this.style.display='none'">
                                            <div>
                                                <div style="{'font-weight: bold;' if team1_winning else ''} font-size: 16px;">
                                                    {team1['team_name']} <span style="font-size: 13px; color: #888; font-weight: normal; margin-left: 5px;">{team1_owner}</span>
                                                </div>
                                                <div style="font-size: 12px; color: #666; margin-top: 2px;">({team1['league_name']}, {team1['wins']}-{team1['losses']}, {team1_seed}{'st' if team1_seed == 1 else 'nd' if team1_seed == 2 else 'rd' if team1_seed == 3 else 'th' if isinstance(team1_seed, int) else ''})</div>
                                            </div>
                                        </div>
                                        <div style="font-size: 24px; font-weight: bold; color: {'#3eab43' if team1_winning else '#666'};">
                                            {team1_score if team1_score is not None else '---'}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)

                                # Team 2
                                st.markdown(f"""
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div style="display: flex; align-items: center; gap: 10px;">
                                            <img src="{team2_logo}" style="width: 30px; height: 30px; border-radius: 50%;" onerror="this.style.display='none'">
                                            <div>
                                                <div style="{'font-weight: bold;' if team2_winning else ''} font-size: 16px;">
                                                    {team2['team_name']} <span style="font-size: 13px; color: #888; font-weight: normal; margin-left: 5px;">{team2_owner}</span>
                                                </div>
                                                <div style="font-size: 12px; color: #666; margin-top: 2px; margin-bottom: 8px;">({team2['league_name']}, {team2['wins']}-{team2['losses']}, {team2_seed}{'st' if team2_seed == 1 else 'nd' if team2_seed == 2 else 'rd' if team2_seed == 3 else 'th' if isinstance(team2_seed, int) else ''})</div>
                                            </div>
                                        </div>
                                        <div style="font-size: 24px; font-weight: bold; color: {'#3eab43' if team2_winning else '#666'};">
                                            {team2_score if team2_score is not None else '---'}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)

                            st.write("")
        else:
            st.info("No matchups available")
    else:
        st.error("Failed to fetch league data")
