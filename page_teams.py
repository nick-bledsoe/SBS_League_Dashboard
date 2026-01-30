from utils import *
from utils_storage import get_storage, get_current_season


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
                        <div style="font-size: 2rem; font-weight: 600; line-height: 1.2;">{get_ordinal(team_seed)}</div>
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
                            for player in position_list:
                                # Get player ID for headshot
                                player_id = player.get('player_id', '')
                                headshot_url = f"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/{player_id}.png&w=96&h=70&cb=1" if player_id else ""
                                nfl_logo = player.get('NFL Logo', '')

                                st.markdown(f"""
                                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px; margin: 4px 0; background-color: rgba(128, 128, 128, 0.05); border-radius: 4px;">
                                        <div style="display: flex; align-items: center; gap: 10px;">
                                            <img src="{headshot_url}" style="width: 35px; height: 26px; border-radius: 4px; object-fit: cover;" onerror="this.style.display='none'">
                                            <div style="flex: 1;">
                                                <div style="font-size: 14px; font-weight: 500;">{player['Player']}</div>
                                                <div style="font-size: 11px; color: #888;">Pos Rank: {player['Rank']}</div>
                                            </div>
                                        </div>
                                        <div style="display: flex; align-items: center;">
                                            <img src="{nfl_logo}" style="width: 30px; height: 30px;" onerror="this.style.display='none'">
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
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
                            'Is Current': week == current_week,
                            'Opponent ID': opponent_id,
                            'Game Type': 'Regular Season'
                        })

                # ADD PLAYOFF GAMES
                from utils_storage import get_current_season
                current_season = get_current_season()
                storage = get_storage(season=current_season)
                playoff_matchups = storage.load_playoff_matchups()

                if playoff_matchups:
                    # Find playoff matchups involving this team
                    for week, matchups in playoff_matchups.items():
                        for matchup in matchups:
                            team1 = matchup['team1']
                            team2 = matchup['team2']
                            matchup_type = matchup.get('type', 'Playoff')

                            # Check if selected team is in this playoff matchup
                            if team1['team_name'] == selected_team['team_name'] and team1['league_name'] == \
                                    selected_team['league_name']:
                                # This team is team1
                                opponent = team2
                                is_team1 = True
                            elif team2['team_name'] == selected_team['team_name'] and team2['league_name'] == \
                                    selected_team['league_name']:
                                # This team is team2
                                opponent = team1
                                is_team1 = False
                            else:
                                # This team is not in this matchup
                                continue

                            # Get scores
                            team_score = get_team_score_for_week(
                                selected_team['league_id'],
                                selected_team['team_name'],
                                week
                            )
                            opp_score = get_team_score_for_week(
                                opponent['league_id'],
                                opponent['team_name'],
                                week
                            )

                            # Get opponent logo
                            opponent_league_data = fetch_league_data(opponent['league_id'])
                            opponent_logo = ""
                            if opponent_league_data and 'teams' in opponent_league_data:
                                for team in opponent_league_data['teams']:
                                    if team.get('id') == opponent['team_id']:
                                        opponent_logo = team.get('logo', '')
                                        break

                            # Determine result
                            if week <= current_week:
                                if team_score is not None and opp_score is not None:
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
                            else:
                                result = "-"
                                result_color = "#666"
                                team_score = "-"
                                opp_score = "-"

                            # Get opponent owner
                            opponent_owner = TEAM_OWNERS.get(opponent['team_name'], "")

                            team_schedule.append({
                                'Week': week,
                                'Opponent': opponent['team_name'],
                                'Opponent Owner': opponent_owner,
                                'Opponent Logo': opponent_logo,
                                'Location': 'vs',  # Playoff games are neutral
                                'Result': result,
                                'Result Color': result_color,
                                'Team Score': team_score,
                                'Opp Score': opp_score,
                                'Is Current': week == current_week,
                                'Opponent ID': opponent['team_id'],
                                'Game Type': matchup_type  # e.g., "Quarterfinal", "Semifinal", "Championship"
                            })

                # Sort by week
                team_schedule.sort(key=lambda x: x['Week'])

                if team_schedule:
                    # Display schedule with expandable scoring details
                    for game in team_schedule:
                        # Determine if this is a playoff game
                        is_playoff = game.get('Game Type', 'Regular Season') != 'Regular Season'
                        game_type_display = game.get('Game Type', 'Regular Season')

                        # Choose color for game type badge
                        if game_type_display == 'Quarterfinal':
                            badge_color = "#ffd700"
                        elif game_type_display == 'Semifinal':
                            badge_color = "#ff6b6b"
                        elif game_type_display == '3rd Place':
                            badge_color = "#4ecdc4"
                        elif game_type_display == 'Championship':
                            badge_color = "#9b59b6"
                        else:
                            badge_color = "#808495"

                        # Show score and W/L in card, with expandable details for completed games
                        if game['Result'] != '-':
                            with st.container(border=True):
                                col1, col2, col3 = st.columns([1, 5, 1])

                                with col1:
                                    # Build the complete HTML for the week column including playoff badge if needed
                                    week_html = f"""
                                        <div style="text-align: center;">
                                            <div style="font-size: 12px; color: #808495; font-weight: 600;">WEEK</div>
                                            <div style="font-size: 24px; font-weight: bold;">{game['Week']}</div>"""

                                    if game['Is Current']:
                                        week_html += '<div style="font-size: 10px; color: #ff4444; font-weight: 600; margin-top: 4px;">CURRENT</div>'

                                    if is_playoff:
                                        week_html += f'<div style="background-color: {badge_color}; color: white; padding: 2px 8px; border-radius: 8px; font-size: 9px; font-weight: 600; margin-top: 4px; text-align: center;">{game_type_display}</div>'

                                    week_html += "</div>"

                                    st.markdown(week_html, unsafe_allow_html=True)

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
                                                <div style="font-size: 18px; font-weight: 600; color: #666;">{game['Team Score']} - {game['Opp Score']}</div>
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)

                                with col3:
                                    st.markdown(f"""
                                        <div style="text-align: center;">
                                            <div style="font-size: 28px; font-weight: bold; color: {game['Result Color']};">{game['Result']}</div>
                                        </div>
                                    """, unsafe_allow_html=True)

                                # Add expandable scoring details (no outline)
                                with st.expander("Scoring Details", expanded=False):
                                    st.markdown("""
                                        <style>
                                        div[data-testid="stExpander"] {
                                            border: none !important;
                                            box-shadow: none !important;
                                        }
                                        div[data-testid="stExpander"] > div {
                                            border: none !important;
                                        }
                                        </style>
                                    """, unsafe_allow_html=True)

                                    render_game_detail(
                                        selected_team['league_id'],
                                        selected_team['team_id'],
                                        game['Opponent ID'],
                                        selected_team['team_name'],
                                        game['Opponent'],
                                        game['Week'],
                                        game['Team Score'],
                                        game['Opp Score']
                                    )
                        else:
                            # For future games, just show the basic card
                            with st.container(border=True):
                                col1, col2, col3 = st.columns([1, 5, 1])

                                with col1:
                                    # Build the complete HTML for the week column including playoff badge if needed
                                    week_html = f"""
                                        <div style="text-align: center;">
                                            <div style="font-size: 12px; color: #808495; font-weight: 600;">WEEK</div>
                                            <div style="font-size: 24px; font-weight: bold;">{game['Week']}</div>"""

                                    if is_playoff:
                                        week_html += f'<div style="background-color: {badge_color}; color: white; padding: 2px 8px; border-radius: 8px; font-size: 9px; font-weight: 600; margin-top: 4px; text-align: center;">{game_type_display}</div>'

                                    week_html += "</div>"

                                    st.markdown(week_html, unsafe_allow_html=True)

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
                                                <div style="font-size: 14px; color: #888;">Not played</div>
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)

                                with col3:
                                    st.markdown("")
                else:
                    st.info("No schedule available for this team")
            else:
                st.warning("Schedule data not available")
        else:
            st.error("Failed to fetch roster data")
    else:
        st.error("Failed to load teams")


def render_game_detail(league_id, team_id, opponent_id, team_name, opponent_name, week, team_score, opp_score):
    """Render detailed scoring breakdown for a game"""
    # Fetch detailed rosters
    matchups = get_matchup_roster_details(league_id, week)

    if not matchups:
        st.info("Detailed scoring not available for this week")
        return

    # Find the matchup with these teams
    team_roster = None
    opp_roster = None

    for matchup in matchups:
        if matchup['home_team']['id'] == team_id:
            team_roster = matchup['home_team']['roster']
            opp_roster = matchup['away_team']['roster']
            break
        elif matchup['away_team']['id'] == team_id:
            team_roster = matchup['away_team']['roster']
            opp_roster = matchup['home_team']['roster']
            break

    if not team_roster or not opp_roster:
        st.info("Roster details not available")
        return

    # Determine winner
    team_won = team_score > opp_score
    opp_won = opp_score > team_score

    # Show side-by-side scoring
    col1, col2 = st.columns(2)

    with col1:
        team_header_style = "font-weight: bold;" if team_won else ""
        st.markdown(f"<div style='font-size: 16px; {team_header_style}'>{team_name} ({team_score})</div>",
                    unsafe_allow_html=True)
        for player in team_roster:
            color = "#3eab43" if player['points'] >= 5 else "#666" if player['points'] >= 0 else "#d32f2f"
            player_id = player.get('player_id', '')
            headshot = f"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/{player_id}.png&w=96&h=70&cb=1" if player_id else ""

            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px; margin: 3px 0;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <img src="{headshot}" style="width: 28px; height: 20px; border-radius: 3px; object-fit: cover;" onerror="this.style.display='none'">
                        <div style="font-size: 13px;">{player['name']} - {player['nfl_team']} - {player['position']}</div>
                    </div>
                    <div style="font-size: 13px; font-weight: bold; color: {color};">{player['points']}</div>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        opp_header_style = "font-weight: bold;" if opp_won else ""
        st.markdown(f"<div style='font-size: 16px; {opp_header_style}'>{opponent_name} ({opp_score})</div>",
                    unsafe_allow_html=True)
        for player in opp_roster:
            color = "#3eab43" if player['points'] >= 5 else "#666" if player['points'] >= 0 else "#d32f2f"
            player_id = player.get('player_id', '')
            headshot = f"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/{player_id}.png&w=96&h=70&cb=1" if player_id else ""

            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px; margin: 3px 0;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <img src="{headshot}" style="width: 28px; height: 20px; border-radius: 3px; object-fit: cover;" onerror="this.style.display='none'">
                        <div style="font-size: 13px;">{player['name']} - {player['nfl_team']} - {player['position']}</div>
                    </div>
                    <div style="font-size: 13px; font-weight: bold; color: {color};">{player['points']}</div>
                </div>
            """, unsafe_allow_html=True)
