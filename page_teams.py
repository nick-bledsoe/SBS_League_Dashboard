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

            if roster:
                qbs = [p for p in roster if p['Position'] == 'QB']
                kickers = [p for p in roster if p['Position'] == 'K']
                punters = [p for p in roster if p['Position'] == 'P']

                col1, col2, col3 = st.columns(3)

                for col, position_name, position_list in [(col1, "Quarterback", qbs), (col2, "Kickers", kickers), (col3, "Punters", punters)]:
                    with col:
                        st.subheader(f":orange[{position_name}]")
                        if position_list:
                            df = pd.DataFrame(position_list)
                            st.dataframe(df[['Player', 'NFL Team', 'Rank']], use_container_width=True, hide_index=True,
                                column_config={
                                    "Player": st.column_config.TextColumn("Player", width="medium"),
                                    "NFL Team": st.column_config.TextColumn("Team", width="small"),
                                    "Rank": st.column_config.TextColumn("Pos Rank", width="small")
                                })
                        else:
                            st.info(f"No {position_name}")
            else:
                st.warning("No roster data available for this team")
        else:
            st.error("Failed to fetch roster data")
    else:
        st.error("Failed to load teams")
