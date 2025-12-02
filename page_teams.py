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

        if league_data:
            roster = get_team_roster(league_data, selected_team['team_id'])

            standings_df = fetch_all_leagues()
            matchups_df = fetch_all_matchups()
            playoff_df = calculate_playoff_standings(standings_df, matchups_df)

            team_seed = "N/A"
            if playoff_df is not None:
                team_row = playoff_df[(playoff_df['Name'] == selected_team['team_name']) &
                                      (playoff_df['League'] == selected_team['league_name'])]
                if not team_row.empty:
                    team_seed = int(team_row.iloc[0]['Rank'])

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
