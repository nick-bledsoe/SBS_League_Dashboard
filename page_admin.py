from utils import *
import streamlit as st
from utils_storage import get_storage, get_current_season
from datetime import datetime

# Playoff matchup type options (removed Regular Season and Wildcard)
MATCHUP_TYPES = [
    "Quarterfinal",
    "Semifinal",
    "3rd Place",
    "Championship"
]

# Colors for matchup types
MATCHUP_TYPE_COLORS = {
    "Quarterfinal": "#ffd700",
    "Semifinal": "#ff6b6b",
    "3rd Place": "#4ecdc4",
    "Championship": "#9b59b6"
}


def render_admin_tab():
    st.markdown("## Admin Panel")
    st.caption("Manage playoff matchups and league settings")

    # Season selector at the top
    st.markdown("---")
    st.markdown("### Season Selection")
    col1, col2 = st.columns([1, 3])

    with col1:
        current_year = get_current_season()
        available_seasons = list(range(2024, current_year + 2))

        selected_season = st.selectbox(
            "Select Season",
            options=available_seasons,
            index=available_seasons.index(current_year) if current_year in available_seasons else len(
                available_seasons) - 1,
            key="season_selector"
        )

    with col2:
        st.markdown(
            f"<div style='margin-top: 28px; color: #808495;'>Managing playoff matchups for the {selected_season} season</div>",
            unsafe_allow_html=True)

    st.markdown("---")

    # Get storage for selected season
    storage = get_storage(season=selected_season)

    # Initialize session state key based on season
    session_key = f'playoff_matchups_{selected_season}'
    if session_key not in st.session_state:
        st.session_state[session_key] = storage.load_playoff_matchups()

    # Get all teams
    all_teams = get_all_teams()

    if not all_teams:
        st.error("Failed to load teams")
        return

    # Get playoff standings for seed information
    standings_df = fetch_all_leagues()
    matchups_df = fetch_all_matchups()
    playoff_df = calculate_playoff_standings(standings_df, matchups_df)

    # Create team options with seed information
    team_options_with_seed = []
    for team in all_teams:
        seed = "N/A"
        if playoff_df is not None:
            team_row = playoff_df[(playoff_df['Name'] == team['team_name'])]
            if not team_row.empty:
                seed_num = int(team_row.iloc[0]['Rank'])
                seed = f"{seed_num}{'st' if seed_num == 1 else 'nd' if seed_num == 2 else 'rd' if seed_num == 3 else 'th'}"

        team_options_with_seed.append(f"{team['team_name']} ({seed})")

    # Edit mode state
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = None

    # Create new matchup section
    st.subheader("Create Playoff Matchup")

    col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1, 1])

    with col1:
        selected_team1 = st.selectbox(
            "Select Team 1",
            options=team_options_with_seed,
            key="matchup_team1"
        )

    with col2:
        selected_team2 = st.selectbox(
            "Select Team 2",
            options=team_options_with_seed,
            key="matchup_team2"
        )

    with col3:
        matchup_type = st.selectbox(
            "Round",
            options=MATCHUP_TYPES,
            key="matchup_type"
        )

    with col4:
        current_week = get_current_week()
        week_options_create = [f"{week} (current)" if week == current_week else str(week) for week in range(1, 19)]
        default_index = min(max(current_week - 1, 0), len(week_options_create) - 1)

        selected_create_week = st.selectbox(
            "Week",
            options=week_options_create,
            index=default_index,
            key="matchup_week_input"
        )
        matchup_week = int(selected_create_week.split()[0])

    with col5:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Create", type="primary", use_container_width=True):
            team1_idx = team_options_with_seed.index(selected_team1)
            team2_idx = team_options_with_seed.index(selected_team2)
            team1_data = all_teams[team1_idx]
            team2_data = all_teams[team2_idx]

            if team1_data['team_name'] == team2_data['team_name'] and team1_data['league_name'] == team2_data[
                'league_name']:
                st.error("Cannot create a matchup with the same team!")
            else:
                if matchup_week not in st.session_state[session_key]:
                    st.session_state[session_key][matchup_week] = []

                exists = any(
                    (m['team1']['team_name'] == team1_data['team_name'] and
                     m['team2']['team_name'] == team2_data['team_name']) or
                    (m['team1']['team_name'] == team2_data['team_name'] and
                     m['team2']['team_name'] == team1_data['team_name'])
                    for m in st.session_state[session_key][matchup_week]
                )

                if exists:
                    st.warning(f"This matchup already exists for week {matchup_week}!")
                else:
                    st.session_state[session_key][matchup_week].append({
                        'team1': team1_data,
                        'team2': team2_data,
                        'type': matchup_type
                    })
                    if storage.save_playoff_matchups(st.session_state[session_key]):
                        st.success(
                            f"Created {matchup_type} matchup for week {matchup_week}: {team1_data['team_name']} vs {team2_data['team_name']}")
                        st.rerun()
                    else:
                        st.error("Failed to save matchup to Google Sheets")

    # Display existing matchups
    st.markdown("---")
    st.subheader("🏆 Playoff Matchups")

    if not st.session_state[session_key] or all(
            len(matchups) == 0 for matchups in st.session_state[session_key].values()):
        st.info("No playoff matchups created yet. Create one above to get started!")
    else:
        current_week = get_current_week()

        all_weeks_with_matchups = sorted(
            [week for week, matchups in st.session_state[session_key].items() if matchups])

        if not all_weeks_with_matchups:
            st.info("No playoff matchups created yet. Create one above to get started!")
            return

        week_options = [f"{week} (current week)" if week == current_week else str(week) for week in
                        all_weeks_with_matchups]

        col1, col2 = st.columns([3, 1])
        with col1:
            selected_week_display = st.selectbox(
                ":grey[Select Week]",
                options=week_options,
                index=len(week_options) - 1 if current_week in all_weeks_with_matchups else 0,
                key="matchup_week_selector"
            )
            selected_week = int(selected_week_display.split()[0])
        with col2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Refresh Scores", use_container_width=True):
                st.rerun()

        st.markdown("")

        if playoff_df is None:
            standings_df = fetch_all_leagues()
            matchups_df = fetch_all_matchups()
            playoff_df = calculate_playoff_standings(standings_df, matchups_df)

        week_matchups = st.session_state[session_key].get(selected_week, [])

        if not week_matchups:
            st.info(f"No matchups for week {selected_week}")
            return

        for idx, matchup in enumerate(week_matchups):
            team1 = matchup['team1']
            team2 = matchup['team2']
            matchup_type = matchup.get('type', 'Championship')

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

            # Check if in edit mode for this matchup
            edit_key = f"{selected_week}_{idx}"
            is_editing = st.session_state.edit_mode == edit_key

            with st.container(border=True):
                # Matchup header with type badge and buttons
                col_header, col_edit, col_delete = st.columns([18, 1, 1])

                with col_header:
                    type_color = MATCHUP_TYPE_COLORS.get(matchup_type, "#9b59b6")
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <h3 style="margin: 0;">Matchup {idx + 1}</h3>
                            <span style="background-color: {type_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">{matchup_type}</span>
                        </div>
                    """, unsafe_allow_html=True)

                with col_edit:
                    if is_editing:
                        if st.button("💾", key=f"save_{edit_key}", help="Save changes"):
                            st.session_state.edit_mode = None
                            storage.save_playoff_matchups(st.session_state[session_key])
                            st.rerun()
                    else:
                        if st.button("✏️", key=f"edit_{edit_key}", help="Edit matchup"):
                            st.session_state.edit_mode = edit_key
                            st.rerun()

                with col_delete:
                    if st.button("🗑", key=f"delete_{edit_key}", help="Delete this matchup"):
                        st.session_state[session_key][selected_week].pop(idx)
                        storage.save_playoff_matchups(st.session_state[session_key])
                        st.rerun()

                # Edit mode
                if is_editing:
                    st.markdown("**Edit Matchup Type**")

                    # Create edit options for matchup type
                    new_type = st.selectbox(
                        "Playoff Round",
                        options=MATCHUP_TYPES,
                        index=MATCHUP_TYPES.index(matchup_type) if matchup_type in MATCHUP_TYPES else 0,
                        key=f"edit_type_{edit_key}"
                    )

                    # Update matchup type if changed
                    st.session_state[session_key][selected_week][idx]['type'] = new_type

                    st.info("Click the save button (💾) to save your changes")

                # Team 1
                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; padding: 10px; border-radius: 8px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <img src="{team1_logo}" style="width: 40px; height: 40px; border-radius: 50%;" onerror="this.style.display='none'">
                            <div>
                                <div style="{'font-weight: bold;' if team1_winning else ''} font-size: 18px;">
                                    {team1['team_name']} <span style="font-size: 14px; color: #888; font-weight: normal; margin-left: 5px;">{team1_owner}</span>
                                </div>
                                <div style="font-size: 13px; color: #666; margin-top: 2px;">({team1['league_name']}, {team1['wins']}-{team1['losses']}, {get_ordinal(team1_seed) if isinstance(team1_seed, int) else team1_seed})</div>
                            </div>
                        </div>
                        <div style="font-size: 32px; font-weight: bold; color: {'#3eab43' if team1_winning else '#666'};">
                            {team1_score if team1_score is not None else '---'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Team 2
                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <img src="{team2_logo}" style="width: 40px; height: 40px; border-radius: 50%;" onerror="this.style.display='none'">
                            <div>
                                <div style="{'font-weight: bold;' if team2_winning else ''} font-size: 18px;">
                                    {team2['team_name']} <span style="font-size: 14px; color: #888; font-weight: normal; margin-left: 5px;">{team2_owner}</span>
                                </div>
                                <div style="font-size: 13px; color: #666; margin-top: 2px;">({team2['league_name']}, {team2['wins']}-{team2['losses']}, {get_ordinal(team2_seed) if isinstance(team2_seed, int) else team2_seed})</div>
                            </div>
                        </div>
                        <div style="font-size: 32px; font-weight: bold; color: {'#3eab43' if team2_winning else '#666'};">
                            {team2_score if team2_score is not None else '---'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("")
