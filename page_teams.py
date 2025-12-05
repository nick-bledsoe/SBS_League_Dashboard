from utils import *


def render_teams_tab():
    st.markdown("")

    all_teams = get_all_teams()

    if all_teams:
        team_options = [f"{team['team_name']} ({team['league_name']})" for team in all_teams]

        selected_team_display = st.selectbox(
            ":grey[Select a team to view roster]",
            options=team_options,
            key="team_selector"
        )

        selected_idx = team_options.index(selected_team_display)
        selected_team = all_teams[selected_idx]

        league_data = fetch_league_data(selected_team['league_id'])

        # Get owner names
        owner = TEAM_OWNERS.get(selected_team['team_name'], "")

        if league_data:
            roster = get_team_roster(league_data, selected_team['team_id'])

            # Get team logo
            team_logo = ""
            if 'teams' in league_data:
                for team in league_data['teams']:
                    if team.get('id') == selected_team['team_id']:
                        team_logo = team.get('logo', '')
                        break

            standings_df = fetch_all_leagues()
            matchups_df = fetch_all_matchups()
            playoff_df = calculate_playoff_standings(standings_df, matchups_df)

            team_seed = "N/A"
            if playoff_df is not None:
                team_row = playoff_df[(playoff_df['Name'] == selected_team['team_name']) &
                                      (playoff_df['League'] == selected_team['league_name'])]
                if not team_row.empty:
                    team_seed = int(team_row.iloc[0]['Rank'])

            # Team header with metrics
            st.markdown(f"""
                <style>
                @media (max-width: 768px) {{
                    .team-metrics {{
                        grid-template-columns: 1fr !important;
                        gap: 16px !important;
                    }}
                }}
                </style>
                <div class="team-metrics" style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div class="team-info" style="display: flex; align-items: center; gap: 12px;">
                        <div>
                            <div style="font-size: 1rem; color: #808495; font-weight: 600;">Team</div>
                            <div style="font-size: 2rem; font-weight: 600; line-height: 1.2;"><img src="{team_logo}" style="width: 35px; height: 35px; border-radius: 50%;" onerror="this.style.display='none'"> {selected_team['team_name']}</div>
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 1rem; color: #808495; font-weight: 600;">Division</div>
                        <div style="font-size: 2rem; font-weight: 600; line-height: 1.2;">{selected_team['league_name']}</div>
                    </div>
                    <div>
                        <div style="font-size: 1rem; color: #808495; font-weight: 600;">Record</div>
                        <div style="font-size: 2rem; font-weight: 600; line-height: 1.2;">{selected_team['wins']}-{selected_team['losses']}</div>
                    </div>
                    <div>
                        <div style="font-size: 1rem; color: #808495; font-weight: 600;">Seed</div>
                        <div style="font-size: 2rem; font-weight: 600; line-height: 1.2;">{team_seed}{'st' if team_seed == 1 else 'nd' if team_seed == 2 else 'rd' if team_seed == 3 else 'th'}</div>
                    </div>
                    <div>
                        <div style="font-size: 1rem; color: #808495; font-weight: 600;">Owner</div>
                        <div style="font-size: 2rem; font-weight: 600; line-height: 1.2;">{owner}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # Roster Section
            st.subheader("Roster")
            if roster:
                qbs = [p for p in roster if p['Position'] == 'QB']
                kickers = [p for p in roster if p['Position'] == 'K']
                punters = [p for p in roster if p['Position'] == 'P']

                col1, col2, col3 = st.columns(3)

                for col, position_name, position_list in [(col1, "Quarterback", qbs), (col2, "Kickers", kickers),
                                                          (col3, "Punters", punters)]:
                    with col:
                        st.markdown(f"**:orange[{position_name}]**")
                        if position_list:
                            # Prepare data with logos for display
                            display_data = []
                            for player in position_list:
                                display_data.append({
                                    'Player': player['Player'],
                                    'Logo': player['NFL Logo'] if player['NFL Logo'] else None,
                                    'Pos Rank': player['Rank']
                                })

                            # Create DataFrame for display
                            df = pd.DataFrame(display_data)

                            # Display with custom column config to show logos
                            st.dataframe(
                                df,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Player": st.column_config.TextColumn("Player", width="medium"),
                                    "Logo": st.column_config.ImageColumn("Team", width="small"),
                                    "Pos Rank": st.column_config.TextColumn("Pos Rank", width="small")
                                }
                            )
                        else:
                            st.info(f"No {position_name}")
            else:
                st.warning("No roster data available for this team")

            # Schedule Section
            st.markdown("---")
            st.subheader("Results")

            if league_data and 'schedule' in league_data:
                schedule = league_data.get('schedule', [])
                teams = league_data.get('teams', [])
                team_map = {team.get('id'): team.get('name', 'Unknown') for team in teams}
                logo_map = {team.get('id'): team.get('logo', '') for team in teams}
                current_week = league_data.get('scoringPeriodId', 1)

                # Filter schedule for selected team
                team_schedule = []
                for matchup in schedule:
                    home = matchup.get('home', {})
                    away = matchup.get('away', {})

                    if not away:  # Skip bye weeks
                        continue

                    home_team_id = home.get('teamId')
                    away_team_id = away.get('teamId')
                    home_team_name = team_map.get(home_team_id, 'Unknown')
                    away_team_name = team_map.get(away_team_id, 'Unknown')

                    # Check if selected team is in this matchup
                    if home_team_name == selected_team['team_name'] or away_team_name == selected_team['team_name']:
                        week = matchup.get('matchupPeriodId')
                        is_home = home_team_name == selected_team['team_name']
                        opponent_name = away_team_name if is_home else home_team_name
                        opponent_id = away_team_id if is_home else home_team_id
                        opponent_logo = logo_map.get(opponent_id, '')

                        # Get scores
                        if week == current_week:
                            team_score = round(home.get('totalPointsLive', 0), 1) if is_home else round(
                                away.get('totalPointsLive', 0), 1)
                            opp_score = round(away.get('totalPointsLive', 0), 1) if is_home else round(
                                home.get('totalPointsLive', 0), 1)
                        else:
                            team_score = round(home.get('totalPoints', 0), 1) if is_home else round(
                                away.get('totalPoints', 0), 1)
                            opp_score = round(away.get('totalPoints', 0), 1) if is_home else round(
                                home.get('totalPoints', 0), 1)

                        # Determine result
                        if week <= current_week:
                            if team_score > opp_score:
                                result = "W"
                                result_color = "#3eab43"
                            elif team_score < opp_score:
                                result = "L"
                                result_color = "#d32f2f"
                            else:
                                result = "T"
                                result_color = "#666"
                        else:
                            result = "-"
                            result_color = "#666"
                            team_score = "-"
                            opp_score = "-"

                        # Get opponent owner
                        opponent_owner = TEAM_OWNERS.get(opponent_name, "")

                        team_schedule.append({
                            'Week': week,
                            'Opponent': opponent_name,
                            'Opponent Owner': opponent_owner,
                            'Opponent Logo': opponent_logo,
                            'Location': 'vs' if is_home else '@',
                            'Result': result,
                            'Result Color': result_color,
                            'Team Score': team_score,
                            'Opp Score': opp_score,
                            'Is Current': week == current_week
                        })

                # Sort by week
                team_schedule.sort(key=lambda x: x['Week'])

                if team_schedule:
                    # Display schedule in a nice format
                    for game in team_schedule:
                        with st.container(border=True):
                            col1, col2, col3 = st.columns([1, 5, 1])

                            with col1:
                                st.markdown(f"""
                                    <div style="text-align: center;">
                                        <div style="font-size: 12px; color: #808495; font-weight: 600;">WEEK</div>
                                        <div style="font-size: 24px; font-weight: bold;">{game['Week']}</div>
                                        {f'<div style="font-size: 10px; color: #ff4444; font-weight: 600; margin-top: 4px;">CURRENT WEEK</div>' if game['Is Current'] else ''}
                                    </div>
                                """, unsafe_allow_html=True)

                            with col2:
                                st.markdown(f"""
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div style="display: flex; align-items: center; gap: 10px;">
                                            <div style="font-size: 18px; color: #666; font-weight: 600; min-width: 30px;">{game['Location']}</div>
                                            <img src="{game['Opponent Logo']}" style="width: 35px; height: 35px; border-radius: 50%;" onerror="this.style.display='none'">
                                            <div>
                                                <div style="font-size: 16px; font-weight: 600;">{game['Opponent']}</div>
                                                <div style="font-size: 13px; color: #888;">{game['Opponent Owner']}</div>
                                            </div>
                                        </div>
                                        <div style="text-align: right;">
                                            {f'<div style="font-size: 18px; color: #666;">{game["Team Score"]} - {game["Opp Score"]}</div>' if game['Result'] != '-' else '<div style="font-size: 14px; color: #888;">Not played</div>'}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)

                            with col3:
                                if game['Result'] != '-':
                                    st.markdown(f"""
                                        <div style="text-align: center;">
                                            <div style="font-size: 28px; font-weight: bold; color: {game['Result Color']};">{game['Result']}</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown("")
                else:
                    st.info("No schedule available for this team")
            else:
                st.warning("Schedule data not available")
        else:
            st.error("Failed to fetch roster data")
    else:
        st.error("Failed to load teams")
