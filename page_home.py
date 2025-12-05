from utils import *


def render_home_tab():
    st.markdown("")

    if st.button("Refresh Data", key="refresh_standings"):
        st.rerun()

    standings_df = fetch_all_leagues()

    if standings_df is not None:
        # Playoff Picture
        st.subheader("🏆 Standings")
        st.caption(
            "Top team from each league automatically qualifies | Max 3 teams per league | +0.5 win bonus for highest single week score.")

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
            available_weeks = sorted(matchups_df['Week'].unique())
            week_options = [f"{week} (current week)" if week == current_week else str(week) for week in available_weeks]

            selected_week_display = st.selectbox(
                ":grey[Select Week]",
                options=week_options,
                index=available_weeks.index(current_week) if current_week in available_weeks else 0,
                key="week_selector"
            )

            selected_week = int(selected_week_display.split()[0])
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
            st.info("No matchups available")
    else:
        st.error("Failed to fetch league data")
