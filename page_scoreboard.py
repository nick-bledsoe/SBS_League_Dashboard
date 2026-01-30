from utils import *
import streamlit as st
from utils_storage import get_storage, get_current_season


def render_scoreboard_tab():
    st.markdown("## League Scoreboard")
    st.caption("View detailed player-by-player scoring breakdowns")

    st.markdown("---")

    # Week and Matchup Type selector
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        current_week = get_current_week()
        week_options = [f"{week} (current)" if week == current_week else str(week) for week in range(1, 19)]
        selected_week_display = st.selectbox(
            "Select Week",
            options=week_options,
            index=current_week - 1 if current_week <= 18 else 0,
            key="detailed_matchup_week_selector"
        )
        selected_week = int(selected_week_display.split()[0])

    with col2:
        # Load playoff matchups
        current_season = get_current_season()
        storage = get_storage(season=current_season)
        playoff_matchups = storage.load_playoff_matchups()

        has_playoff_matchups = bool(
            playoff_matchups and selected_week in playoff_matchups and playoff_matchups[selected_week]
        )

        matchup_type = st.selectbox(
            "Matchup Type",
            options=["Regular Season", "Playoffs"],
            index=1 if has_playoff_matchups else 0,
            key="detailed_matchup_type_selector"
        )

    with col3:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Refresh Scores", use_container_width=True, key="detailed_refresh"):
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")

    if matchup_type == "Playoffs":
        # Display playoff matchups
        if not has_playoff_matchups:
            st.info("No playoff matchups for this week. Go to Admin tab to create them.")
            return

        week_playoff_matchups = playoff_matchups.get(selected_week, [])

        # Matchup type colors
        MATCHUP_TYPE_COLORS = {
            "Quarterfinal": "#ffd700",
            "Semifinal": "#ff6b6b",
            "3rd Place": "#4ecdc4",
            "Championship": "#9b59b6"
        }

        # Display playoff matchups across columns (same as Home page)
        num_matchups = len(week_playoff_matchups)
        cols = st.columns(min(3, num_matchups))

        for idx, matchup in enumerate(week_playoff_matchups):
            with cols[idx % 3]:
                team1 = matchup['team1']
                team2 = matchup['team2']
                matchup_round = matchup.get('type', 'Playoff')
                round_color = MATCHUP_TYPE_COLORS.get(matchup_round, "#9b59b6")

                # Fetch detailed rosters for both teams
                team1_roster = get_team_matchup_roster(team1['league_id'], team1['team_id'], selected_week)
                team2_roster = get_team_matchup_roster(team2['league_id'], team2['team_id'], selected_week)

                # Get scores
                team1_score = get_team_score_for_week(team1['league_id'], team1['team_name'], selected_week) or 0
                team2_score = get_team_score_for_week(team2['league_id'], team2['team_name'], selected_week) or 0

                team1_winning = team1_score > team2_score
                team2_winning = team2_score > team1_score

                # Get team logos
                team1_logo = get_team_logo(team1['league_id'], team1['team_id'])
                team2_logo = get_team_logo(team2['league_id'], team2['team_id'])

                # Get owner names
                team1_owner = TEAM_OWNERS.get(team1['team_name'], "")
                team2_owner = TEAM_OWNERS.get(team2['team_name'], "")

                with st.container(border=True):
                    # Matchup type badge
                    st.markdown(f"""
                        <div style="text-align: center; margin-bottom: 8px;">
                            <span style="background-color: {round_color}; color: white; padding: 4px 16px; border-radius: 12px; font-size: 13px; font-weight: 600;">{matchup_round}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    # Team 1
                    st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <img src="{team1_logo}" style="width: 30px; height: 30px; border-radius: 50%;" onerror="this.style.display='none'">
                                <div>
                                    <div style="{'font-weight: bold;' if team1_winning else ''} font-size: 16px;">
                                        {team1['team_name']} <span style="font-size: 13px; color: #888; font-weight: normal; margin-left: 5px;">{team1_owner}</span>
                                    </div>
                                    <div style="font-size: 12px; color: #666; margin-top: 2px;">({team1['league_name']}, {team1['wins']}-{team1['losses']})</div>
                                </div>
                            </div>
                            <div style="font-size: 24px; font-weight: bold; color: {'#3eab43' if team1_winning else '#666'};">
                                {team1_score}
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
                                    <div style="font-size: 12px; color: #666; margin-top: 2px; margin-bottom: 8px;">({team2['league_name']}, {team2['wins']}-{team2['losses']})</div>
                                </div>
                            </div>
                            <div style="font-size: 24px; font-weight: bold; color: {'#3eab43' if team2_winning else '#666'};">
                                {team2_score}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Full Box Score dropdown
                    with st.expander("Full Box Score", expanded=False):
                        if team1_roster and team2_roster:
                            col_roster1, col_roster2 = st.columns(2)

                            with col_roster1:
                                st.markdown(f"**{team1['team_name']}**")
                                for player in team1_roster:
                                    color = "#3eab43" if player['points'] >= 5 else "#666" if player[
                                                                                                  'points'] >= 0 else "#d32f2f"
                                    player_id = player.get('player_id', '')
                                    headshot = f"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/{player_id}.png&w=96&h=70&cb=1" if player_id else ""

                                    st.markdown(f"""
                                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 4px; margin: 2px 0;">
                                            <div style="display: flex; align-items: center; gap: 6px;">
                                                <img src="{headshot}" style="width: 25px; height: 18px; border-radius: 3px; object-fit: cover;" onerror="this.style.display='none'">
                                                <div>
                                                    <div style="font-size: 12px; font-weight: 500;">{player['name']}</div>
                                                    <div style="font-size: 10px; color: #888;">{player['nfl_team']} - {player['position']}</div>
                                                </div>
                                            </div>
                                            <div style="font-size: 12px; font-weight: bold; color: {color};">{player['points']}</div>
                                        </div>
                                    """, unsafe_allow_html=True)

                                # Total
                                total1 = sum(p['points'] for p in team1_roster)
                                st.markdown(f"""
                                    <div style="border-top: 2px solid #666; padding-top: 8px; margin-top: 8px;">
                                        <div style="display: flex; justify-content: space-between; font-weight: bold;">
                                            <div>Total</div>
                                            <div>{total1:.2f}</div>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)

                            with col_roster2:
                                st.markdown(f"**{team2['team_name']}**")
                                for player in team2_roster:
                                    color = "#3eab43" if player['points'] >= 5 else "#666" if player[
                                                                                                  'points'] >= 0 else "#d32f2f"
                                    player_id = player.get('player_id', '')
                                    headshot = f"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/{player_id}.png&w=96&h=70&cb=1" if player_id else ""

                                    st.markdown(f"""
                                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 4px; margin: 2px 0;">
                                            <div style="display: flex; align-items: center; gap: 6px;">
                                                <img src="{headshot}" style="width: 25px; height: 18px; border-radius: 3px; object-fit: cover;" onerror="this.style.display='none'">
                                                <div>
                                                    <div style="font-size: 12px; font-weight: 500;">{player['name']}</div>
                                                    <div style="font-size: 10px; color: #888;">{player['nfl_team']} - {player['position']}</div>
                                                </div>
                                            </div>
                                            <div style="font-size: 12px; font-weight: bold; color: {color};">{player['points']}</div>
                                        </div>
                                    """, unsafe_allow_html=True)

                                # Total
                                total2 = sum(p['points'] for p in team2_roster)
                                st.markdown(f"""
                                    <div style="border-top: 2px solid #666; padding-top: 8px; margin-top: 8px;">
                                        <div style="display: flex; justify-content: space-between; font-weight: bold;">
                                            <div>Total</div>
                                            <div>{total2:.2f}</div>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("Roster data not available")

                st.write("")

    else:
        # Fetch regular season matchups from ALL leagues
        all_matchups = []

        for league_name, league_id in LEAGUES.items():
            with st.spinner(f"Loading {league_name} matchups..."):
                matchups = get_matchup_roster_details(league_id, selected_week)
                if matchups:
                    for matchup in matchups:
                        matchup['league_name'] = league_name
                    all_matchups.extend(matchups)

        if not all_matchups:
            st.warning(f"No matchups found for week {selected_week}")
            return

        # Display regular season matchups in columns (same as Home page)
        cols = st.columns(3)

        # Group matchups by league
        for idx, league_name in enumerate(LEAGUES.keys()):
            with cols[idx]:
                league_matchups = [m for m in all_matchups if m['league_name'] == league_name]
                st.markdown(f"### :orange[{league_name}]")

                if not league_matchups:
                    st.info(f"No matchups for week {selected_week}")
                else:
                    for matchup in league_matchups:
                        home_team = matchup['home_team']
                        away_team = matchup['away_team']

                        home_winning = home_team['total_points'] > away_team['total_points']
                        away_winning = away_team['total_points'] > home_team['total_points']

                        # Get owner names
                        home_owner = TEAM_OWNERS.get(home_team['name'], "")
                        away_owner = TEAM_OWNERS.get(away_team['name'], "")

                        with st.container(border=True):
                            # Home team
                            st.markdown(f"""
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <img src="{home_team['logo']}" style="width: 30px; height: 30px; border-radius: 50%;" onerror="this.style.display='none'">
                                        <div>
                                            <div style="{'font-weight: bold;' if home_winning else ''} font-size: 16px;">
                                                {home_team['name']} <span style="font-size: 13px; color: #888; font-weight: normal; margin-left: 5px;">{home_owner}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div style="font-size: 24px; font-weight: bold; color: {'#3eab43' if home_winning else '#666'};">{home_team['total_points']:.1f}</div>
                                </div>
                            """, unsafe_allow_html=True)

                            # Away team
                            st.markdown(f"""
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <img src="{away_team['logo']}" style="width: 30px; height: 30px; border-radius: 50%;" onerror="this.style.display='none'">
                                        <div>
                                            <div style="{'font-weight: bold;' if away_winning else ''} font-size: 16px;">
                                                {away_team['name']} <span style="font-size: 13px; color: #888; font-weight: normal; margin-left: 5px;">{away_owner}</span>
                                            </div>
                                            <div style="font-size: 12px; color: #666; margin-top: 2px; margin-bottom: 8px;"></div>
                                        </div>
                                    </div>
                                    <div style="font-size: 24px; font-weight: bold; color: {'#3eab43' if away_winning else '#666'};">{away_team['total_points']:.1f}</div>
                                </div>
                            """, unsafe_allow_html=True)

                            # Full Box Score dropdown
                            with st.expander("Full Box Score", expanded=False):
                                if home_team['roster'] and away_team['roster']:
                                    col_roster1, col_roster2 = st.columns(2)

                                    with col_roster1:
                                        st.markdown(f"**{home_team['name']}**")
                                        for player in home_team['roster']:
                                            color = "#3eab43" if player['points'] >= 5 else "#666" if player[
                                                                                                          'points'] >= 0 else "#d32f2f"
                                            player_id = player.get('player_id', '')
                                            headshot = f"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/{player_id}.png&w=96&h=70&cb=1" if player_id else ""

                                            st.markdown(f"""
                                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 4px; margin: 2px 0;">
                                                    <div style="display: flex; align-items: center; gap: 6px;">
                                                        <img src="{headshot}" style="width: 25px; height: 18px; border-radius: 3px; object-fit: cover;" onerror="this.style.display='none'">
                                                        <div>
                                                            <div style="font-size: 12px; font-weight: 500;">{player['name']}</div>
                                                            <div style="font-size: 10px; color: #888;">{player['nfl_team']} - {player['position']}</div>
                                                        </div>
                                                    </div>
                                                    <div style="font-size: 12px; font-weight: bold; color: {color};">{player['points']}</div>
                                                </div>
                                            """, unsafe_allow_html=True)

                                        # Total
                                        total_home = sum(p['points'] for p in home_team['roster'])
                                        st.markdown(f"""
                                            <div style="border-top: 2px solid #666; padding-top: 8px; margin-top: 8px;">
                                                <div style="display: flex; justify-content: space-between; font-weight: bold;">
                                                    <div>Total</div>
                                                    <div>{total_home:.2f}</div>
                                                </div>
                                            </div>
                                        """, unsafe_allow_html=True)

                                    with col_roster2:
                                        st.markdown(f"**{away_team['name']}**")
                                        for player in away_team['roster']:
                                            color = "#3eab43" if player['points'] >= 5 else "#666" if player[
                                                                                                          'points'] >= 0 else "#d32f2f"
                                            player_id = player.get('player_id', '')
                                            headshot = f"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/{player_id}.png&w=96&h=70&cb=1" if player_id else ""

                                            st.markdown(f"""
                                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 4px; margin: 2px 0;">
                                                    <div style="display: flex; align-items: center; gap: 6px;">
                                                        <img src="{headshot}" style="width: 25px; height: 18px; border-radius: 3px; object-fit: cover;" onerror="this.style.display='none'">
                                                        <div>
                                                            <div style="font-size: 12px; font-weight: 500;">{player['name']}</div>
                                                            <div style="font-size: 10px; color: #888;">{player['nfl_team']} - {player['position']}</div>
                                                        </div>
                                                    </div>
                                                    <div style="font-size: 12px; font-weight: bold; color: {color};">{player['points']}</div>
                                                </div>
                                            """, unsafe_allow_html=True)

                                        # Total
                                        total_away = sum(p['points'] for p in away_team['roster'])
                                        st.markdown(f"""
                                            <div style="border-top: 2px solid #666; padding-top: 8px; margin-top: 8px;">
                                                <div style="display: flex; justify-content: space-between; font-weight: bold;">
                                                    <div>Total</div>
                                                    <div>{total_away:.2f}</div>
                                                </div>
                                            </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.info("Roster data not available")

                        st.write("")

        # WEEKLY STATS SECTIONS
        st.markdown("---")
        st.markdown("## Week {} Stats".format(selected_week))

        # Collect all player performances and team scores from the week
        all_players = []
        all_team_scores = []

        if matchup_type == "Regular Season":
            # Use regular season matchups
            for matchup in all_matchups:
                home_team = matchup['home_team']
                away_team = matchup['away_team']
                league_name = matchup['league_name']

                # Collect team scores
                all_team_scores.append({
                    'team_name': home_team['name'],
                    'owner': TEAM_OWNERS.get(home_team['name'], ""),
                    'league': league_name,
                    'score': home_team['total_points'],
                    'logo': home_team['logo'],
                    'opponent': away_team['name'],
                    'opponent_score': away_team['total_points']
                })
                all_team_scores.append({
                    'team_name': away_team['name'],
                    'owner': TEAM_OWNERS.get(away_team['name'], ""),
                    'league': league_name,
                    'score': away_team['total_points'],
                    'logo': away_team['logo'],
                    'opponent': home_team['name'],
                    'opponent_score': home_team['total_points']
                })

                # Collect player performances
                for player in home_team['roster']:
                    all_players.append({
                        'name': player['name'],
                        'team': home_team['name'],
                        'nfl_team': player['nfl_team'],
                        'position': player['position'],
                        'points': player['points'],
                        'player_id': player.get('player_id', ''),
                        'team_logo': home_team['logo']
                    })
                for player in away_team['roster']:
                    all_players.append({
                        'name': player['name'],
                        'team': away_team['name'],
                        'nfl_team': player['nfl_team'],
                        'position': player['position'],
                        'points': player['points'],
                        'player_id': player.get('player_id', ''),
                        'team_logo': away_team['logo']
                    })
        else:
            # Use playoff matchups
            for matchup in week_playoff_matchups:
                team1 = matchup['team1']
                team2 = matchup['team2']

                team1_roster = get_team_matchup_roster(team1['league_id'], team1['team_id'], selected_week)
                team2_roster = get_team_matchup_roster(team2['league_id'], team2['team_id'], selected_week)

                team1_score = get_team_score_for_week(team1['league_id'], team1['team_name'], selected_week) or 0
                team2_score = get_team_score_for_week(team2['league_id'], team2['team_name'], selected_week) or 0

                team1_logo = get_team_logo(team1['league_id'], team1['team_id'])
                team2_logo = get_team_logo(team2['league_id'], team2['team_id'])

                # Collect team scores
                all_team_scores.append({
                    'team_name': team1['team_name'],
                    'owner': TEAM_OWNERS.get(team1['team_name'], ""),
                    'league': team1['league_name'],
                    'score': team1_score,
                    'logo': team1_logo,
                    'opponent': team2['team_name'],
                    'opponent_score': team2_score
                })
                all_team_scores.append({
                    'team_name': team2['team_name'],
                    'owner': TEAM_OWNERS.get(team2['team_name'], ""),
                    'league': team2['league_name'],
                    'score': team2_score,
                    'logo': team2_logo,
                    'opponent': team1['team_name'],
                    'opponent_score': team1_score
                })

                # Collect player performances
                for player in team1_roster:
                    all_players.append({
                        'name': player['name'],
                        'team': team1['team_name'],
                        'nfl_team': player['nfl_team'],
                        'position': player['position'],
                        'points': player['points'],
                        'player_id': player.get('player_id', ''),
                        'team_logo': team1_logo
                    })
                for player in team2_roster:
                    all_players.append({
                        'name': player['name'],
                        'team': team2['team_name'],
                        'nfl_team': player['nfl_team'],
                        'position': player['position'],
                        'points': player['points'],
                        'player_id': player.get('player_id', ''),
                        'team_logo': team2_logo
                    })

        # 1. TOP PERFORMERS OF THE WEEK
        st.markdown("### Top Performers of the Week")
        if all_players:
            # Group players by name and combine their teams
            player_dict = {}
            for player in all_players:
                player_name = player['name']
                if player_name not in player_dict:
                    player_dict[player_name] = {
                        'name': player_name,
                        'nfl_team': player['nfl_team'],
                        'position': player['position'],
                        'points': player['points'],
                        'player_id': player['player_id'],
                        'teams': [player['team']],
                        'team_logos': [player['team_logo']]
                    }
                else:
                    # Player appears on multiple fantasy teams, add to list
                    if player['team'] not in player_dict[player_name]['teams']:
                        player_dict[player_name]['teams'].append(player['team'])
                        player_dict[player_name]['team_logos'].append(player['team_logo'])

            # Sort by points and get top 5 unique players
            unique_players = list(player_dict.values())
            top_players = sorted(unique_players, key=lambda x: x['points'], reverse=True)[:5]

            for idx, player in enumerate(top_players):
                headshot = f"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/{player['player_id']}.png&w=96&h=70&cb=1" if \
                player['player_id'] else ""

                # Build teams display
                teams_display = ", ".join(player['teams'])

                with st.container(border=True):
                    col1, col2, col3 = st.columns([1, 4, 1])

                    with col1:
                        st.markdown(f"""
                            <div style="text-align: center;">
                                <div style="font-size: 32px; font-weight: bold; color: #ffd700;">#{idx + 1}</div>
                            </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        # Build team logos HTML
                        logos_html = ""
                        for logo in player['team_logos']:
                            logos_html += f'<img src="{logo}" style="width: 30px; height: 30px; border-radius: 50%; margin-left: 4px;" onerror="this.style.display=\'none\'">'

                        st.markdown(f"""
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <img src="{headshot}" style="width: 50px; height: 37px; border-radius: 4px; object-fit: cover;" onerror="this.style.display='none'">
                                <div style="flex: 1;">
                                    <div style="font-size: 18px; font-weight: 600;">{player['name']}</div>
                                    <div style="font-size: 13px; color: #888;">{player['nfl_team']} - {player['position']} • {teams_display}</div>
                                </div>
                                <div style="display: flex; gap: 2px;">
                                    {logos_html}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                    with col3:
                        st.markdown(f"""
                            <div style="text-align: center;">
                                <div style="font-size: 28px; font-weight: bold; color: #3eab43;">{player['points']}</div>
                                <div style="font-size: 11px; color: #888;">PTS</div>
                            </div>
                        """, unsafe_allow_html=True)

        st.markdown("---")

        # 2. WEEKLY LEAGUE LEADERS
        st.markdown("### Weekly League Leaders")
        st.caption("Highest scoring team from each league this week")

        col1, col2, col3 = st.columns(3)

        for idx, league_name in enumerate(LEAGUES.keys()):
            with [col1, col2, col3][idx]:
                league_teams = [t for t in all_team_scores if t['league'] == league_name]
                if league_teams:
                    top_team = max(league_teams, key=lambda x: x['score'])

                    st.markdown(f"#### :orange[{league_name}]")
                    with st.container(border=True):
                        st.markdown(f"""
                            <div style="text-align: center; padding: 10px;">
                                <img src="{top_team['logo']}" style="width: 60px; height: 60px; border-radius: 50%; margin-bottom: 10px;" onerror="this.style.display='none'">
                                <div style="font-size: 18px; font-weight: 600;">{top_team['team_name']}</div>
                                <div style="font-size: 13px; color: #888; margin-bottom: 8px;">{top_team['owner']}</div>
                                <div style="font-size: 32px; font-weight: bold; color: #3eab43;">{top_team['score']:.1f}</div>
                                <div style="font-size: 11px; color: #888;">POINTS</div>
                            </div>
                        """, unsafe_allow_html=True)

        st.markdown("---")

        # 3. CLOSE GAMES
        st.markdown("### Close Games")
        st.caption("Games decided by 3 points or less")

        close_games = [t for t in all_team_scores if abs(t['score'] - t['opponent_score']) <= 3 and t['score'] > 0]
        # Remove duplicates (each game appears twice)
        seen_matchups = set()
        unique_close_games = []
        for game in close_games:
            matchup_key = tuple(sorted([game['team_name'], game['opponent']]))
            if matchup_key not in seen_matchups:
                seen_matchups.add(matchup_key)
                unique_close_games.append(game)

        if unique_close_games:
            cols = st.columns(min(3, len(unique_close_games)))
            for idx, game in enumerate(unique_close_games):
                with cols[idx % 3]:
                    margin = abs(game['score'] - game['opponent_score'])
                    winner = game['team_name'] if game['score'] > game['opponent_score'] else game['opponent']

                    with st.container(border=True):
                        st.markdown(f"""
                            <div style="text-align: center; padding: 8px;">
                                <div style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">{game['league']}</div>
                                <div style="font-size: 16px; margin-bottom: 4px;">{game['team_name']} vs {game['opponent']}</div>
                                <div style="font-size: 24px; font-weight: bold; color: #ff6b6b; margin: 8px 0;">
                                    {game['score']:.1f} - {game['opponent_score']:.1f}
                                </div>
                                <div style="font-size: 12px; color: #888;">Margin: {margin:.1f} pts</div>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No close games this week")

        st.markdown("---")

        # 4. BLOWOUTS
        st.markdown("### Biggest Blowouts")
        st.caption("Largest margins of victory")

        # Calculate margins and get top 3
        margins = []
        seen_matchups = set()
        for game in all_team_scores:
            if game['score'] > 0:
                matchup_key = tuple(sorted([game['team_name'], game['opponent']]))
                if matchup_key not in seen_matchups:
                    seen_matchups.add(matchup_key)
                    margin = abs(game['score'] - game['opponent_score'])
                    winner = game['team_name'] if game['score'] > game['opponent_score'] else game['opponent']
                    winner_score = max(game['score'], game['opponent_score'])
                    loser = game['opponent'] if game['score'] > game['opponent_score'] else game['team_name']
                    loser_score = min(game['score'], game['opponent_score'])

                    margins.append({
                        'winner': winner,
                        'winner_score': winner_score,
                        'loser': loser,
                        'loser_score': loser_score,
                        'margin': margin,
                        'league': game['league']
                    })

        top_blowouts = sorted(margins, key=lambda x: x['margin'], reverse=True)[:3]

        if top_blowouts:
            cols = st.columns(min(3, len(top_blowouts)))
            for idx, game in enumerate(top_blowouts):
                with cols[idx]:
                    with st.container(border=True):
                        st.markdown(f"""
                            <div style="text-align: center; padding: 8px;">
                                <div style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">{game['league']}</div>
                                <div style="font-size: 16px; margin-bottom: 4px; color: #3eab43; font-weight: 600;">{game['winner']}</div>
                                <div style="font-size: 24px; font-weight: bold; margin: 8px 0;">
                                    {game['winner_score']:.1f} - {game['loser_score']:.1f}
                                </div>
                                <div style="font-size: 14px; color: #d32f2f; margin-bottom: 4px;">{game['loser']}</div>
                                <div style="font-size: 12px; color: #888;">Margin: {game['margin']:.1f} pts</div>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No blowouts this week")

        st.markdown("---")

        # 5. TOTAL POINTS SUMMARY
        st.markdown("### Week {} Summary".format(selected_week))

        if all_team_scores:
            total_points = sum(t['score'] for t in all_team_scores)
            avg_points = total_points / len(all_team_scores) if all_team_scores else 0

            # Calculate per-league stats
            league_totals = {}
            for league_name in LEAGUES.keys():
                league_teams = [t for t in all_team_scores if t['league'] == league_name]
                if league_teams:
                    league_totals[league_name] = sum(t['score'] for t in league_teams)

            highest_scoring_league = max(league_totals.items(), key=lambda x: x[1]) if league_totals else (None, 0)
            lowest_scoring_league = min(league_totals.items(), key=lambda x: x[1]) if league_totals else (None, 0)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Points Scored", f"{total_points:.1f}")

            with col2:
                st.metric("Average Points Per Team", f"{avg_points:.1f}")

            with col3:
                if highest_scoring_league[0]:
                    st.metric("Highest Scoring League", highest_scoring_league[0],
                              f"{highest_scoring_league[1]:.1f} pts")

            with col4:
                if lowest_scoring_league[0]:
                    st.metric("Lowest Scoring League", lowest_scoring_league[0], f"{lowest_scoring_league[1]:.1f} pts")


def render_scoreboard_detail(team1_name, team1_logo, team1_score, team1_winning, team1_roster,
                          team2_name, team2_logo, team2_score, team2_winning, team2_roster):
    """Render the detailed matchup view"""
    # Matchup header
    col_head1, col_head2, col_head3 = st.columns([2, 1, 2])

    with col_head1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="{team1_logo}" style="width: 40px; height: 40px; border-radius: 50%;" onerror="this.style.display='none'">
                <div>
                    <div style="font-size: 18px; font-weight: {'bold' if team1_winning else 'normal'};">
                        {team1_name}
                    </div>
                    <div style="font-size: 14px; color: #666;">
                        {TEAM_OWNERS.get(team1_name, '')}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_head2:
        st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
                    <div style="font-size: 32px; font-weight: bold; color: {'#3eab43' if team1_winning else '#666'};">
                        {team1_score}
                    </div>
                    <div style="font-size: 14px; color: #666;">-</div>
                    <div style="font-size: 32px; font-weight: bold; color: {'#3eab43' if team2_winning else '#666'};">
                        {team2_score}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_head3:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; justify-content: flex-end;">
                <div style="text-align: right;">
                    <div style="font-size: 18px; font-weight: {'bold' if team2_winning else 'normal'};">
                        {team2_name}
                    </div>
                    <div style="font-size: 14px; color: #666;">
                        {TEAM_OWNERS.get(team2_name, '')}
                    </div>
                </div>
                <img src="{team2_logo}" style="width: 40px; height: 40px; border-radius: 50%;" onerror="this.style.display='none'">
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Player breakdown - side by side
    col_home, col_away = st.columns(2)

    with col_home:
        st.markdown(f"**{team1_name} Roster**")
        render_roster_table(team1_roster)

    with col_away:
        st.markdown(f"**{team2_name} Roster**")
        render_roster_table(team2_roster)


def render_roster_table(roster):
    """Render a team's roster as a formatted table"""
    if not roster:
        st.info("No roster data available")
        return

    # All players are starters (no bench)
    for player in roster:
        # Color code by points
        if player['points'] >= 5:
            color = "#3eab43"  # Green for good performance
        elif player['points'] >= 0:
            color = "#666"  # Gray for average
        else:
            color = "#d32f2f"  # Red for negative

        # Get player headshot
        player_id = player.get('player_id', '')
        headshot_url = f"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/{player_id}.png&w=96&h=70&cb=1" if player_id else ""

        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px; margin: 4px 0; background-color: rgba(128, 128, 128, 0.05); border-radius: 4px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <img src="{headshot_url}" style="width: 40px; height: 30px; border-radius: 4px; object-fit: cover;" onerror="this.style.display='none'">
                    <div>
                        <div style="font-size: 14px; font-weight: 500;">{player['name']}</div>
                        <div style="font-size: 11px; color: #888;">{player['nfl_team']} - {player['position']}</div>
                    </div>
                </div>
                <div style="font-size: 16px; font-weight: bold; color: {color};">
                    {player['points']}
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Show total
    total = sum(p['points'] for p in roster)
    st.markdown(f"""
        <div style="padding: 8px; margin-top: 8px; border-top: 2px solid #666;">
            <div style="display: flex; justify-content: space-between; font-weight: bold;">
                <div>TOTAL</div>
                <div style="font-size: 18px;">{total:.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def get_team_matchup_roster(league_id, team_id, week):
    """Get roster for a specific team in a specific week"""
    matchups = get_matchup_roster_details(league_id, week)
    if not matchups:
        return []

    for matchup in matchups:
        if matchup['home_team']['id'] == team_id:
            return matchup['home_team']['roster']
        elif matchup['away_team']['id'] == team_id:
            return matchup['away_team']['roster']

    return []


def get_team_logo(league_id, team_id):
    """Get team logo"""
    league_data = fetch_league_data(league_id)
    if league_data and 'teams' in league_data:
        for team in league_data['teams']:
            if team.get('id') == team_id:
                return team.get('logo', '')
    return ''
