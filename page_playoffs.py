from utils import *
import streamlit as st
import json
import os

MATCHUPS_FILE = "playoff_matchups.json"


def load_matchups_from_file():
    """Load matchups from JSON file"""
    if os.path.exists(MATCHUPS_FILE):
        try:
            with open(MATCHUPS_FILE, 'r') as f:
                data = json.load(f)
                # Convert string keys back to integers
                return {int(k): v for k, v in data.items()}
        except Exception as e:
            st.error(f"Failed to load matchups: {e}")
            return {}
    return {}


def save_matchups_to_file(matchups):
    """Save matchups to JSON file"""
    try:
        with open(MATCHUPS_FILE, 'w') as f:
            json.dump(matchups, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Failed to save matchups: {e}")
        return False


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


def render_playoffs_tab():
    # Initialize session state from file if it doesn't exist
    if 'playoff_matchups' not in st.session_state:
        st.session_state.playoff_matchups = load_matchups_from_file()

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

    # Create new matchup section
    st.subheader("Create New Matchup")

    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

    with col1:
        selected_team1 = st.selectbox(
            "Select Team 1",
            options=team_options_with_seed,
            key="playoff_team1"
        )

    with col2:
        selected_team2 = st.selectbox(
            "Select Team 2",
            options=team_options_with_seed,
            key="playoff_team2"
        )

    with col3:
        current_week = get_current_week()
        # Create week options with current week indicator
        week_options_create = [f"{week} (current)" if week == current_week else str(week) for week in range(1, 19)]

        selected_create_week = st.selectbox(
            "Week",
            options=week_options_create,
            index=current_week - 1,  # Default to current week
            key="matchup_week_input"
        )
        matchup_week = int(selected_create_week.split()[0])

    with col4:
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
                # Initialize week if it doesn't exist
                if matchup_week not in st.session_state.playoff_matchups:
                    st.session_state.playoff_matchups[matchup_week] = []

                # Check if matchup already exists for this week
                exists = any(
                    (m['team1']['team_name'] == team1_data['team_name'] and
                     m['team2']['team_name'] == team2_data['team_name']) or
                    (m['team1']['team_name'] == team2_data['team_name'] and
                     m['team2']['team_name'] == team1_data['team_name'])
                    for m in st.session_state.playoff_matchups[matchup_week]
                )

                if exists:
                    st.warning(f"This matchup already exists for week {matchup_week}!")
                else:
                    st.session_state.playoff_matchups[matchup_week].append({
                        'team1': team1_data,
                        'team2': team2_data
                    })
                    # Save to file after creating matchup
                    if save_matchups_to_file(st.session_state.playoff_matchups):
                        st.success(
                            f"Created matchup for week {matchup_week}: {team1_data['team_name']} vs {team2_data['team_name']}")
                        st.rerun()

    # Display existing matchups
    st.markdown("---")
    st.subheader("🏆 Playoff Matchups")

    if not st.session_state.playoff_matchups or all(
            len(matchups) == 0 for matchups in st.session_state.playoff_matchups.values()):
        st.info("No matchups created yet. Create one above to get started!")
    else:
        current_week = get_current_week()

        # Week selector for viewing different weeks
        all_weeks_with_matchups = sorted(
            [week for week, matchups in st.session_state.playoff_matchups.items() if matchups])

        if not all_weeks_with_matchups:
            st.info("No matchups created yet. Create one above to get started!")
            return

        week_options = [f"{week} (current week)" if week == current_week else str(week) for week in
                        all_weeks_with_matchups]

        col1, col2 = st.columns([3, 1])
        with col1:
            selected_week_display = st.selectbox(
                ":grey[Select Week]",
                options=week_options,
                index=len(week_options) - 1 if current_week in all_weeks_with_matchups else 0,
                key="playoff_week_selector"
            )
            selected_week = int(selected_week_display.split()[0])
        with col2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Refresh Scores", use_container_width=True):
                st.rerun()

        st.markdown("")

        # Get playoff standings for seed information (reuse if already loaded)
        if playoff_df is None:
            standings_df = fetch_all_leagues()
            matchups_df = fetch_all_matchups()
            playoff_df = calculate_playoff_standings(standings_df, matchups_df)

        # Display matchups for selected week
        week_matchups = st.session_state.playoff_matchups.get(selected_week, [])

        if not week_matchups:
            st.info(f"No matchups for week {selected_week}")
            return

        for idx, matchup in enumerate(week_matchups):
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
                # Matchup header with delete button
                col_header, col_delete = st.columns([20, 1])
                with col_header:
                    st.markdown(f"### Matchup {idx + 1}")
                with col_delete:
                    if st.button("🗑", key=f"delete_{selected_week}_{idx}", help="Delete this matchup"):
                        st.session_state.playoff_matchups[selected_week].pop(idx)
                        # Save to file after deleting matchup
                        save_matchups_to_file(st.session_state.playoff_matchups)
                        st.rerun()

                # Team 1
                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; padding: 10px; border-radius: 8px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <img src="{team1_logo}" style="width: 40px; height: 40px; border-radius: 50%;" onerror="this.style.display='none'">
                            <div>
                                <div style="{'font-weight: bold;' if team1_winning else ''} font-size: 18px;">
                                    {team1['team_name']} <span style="font-size: 14px; color: #888; font-weight: normal; margin-left: 5px;">{team1_owner}</span>
                                </div>
                                <div style="font-size: 13px; color: #666; margin-top: 2px;">({team1['league_name']}, {team1['wins']}-{team1['losses']}, {team1_seed}{'st' if team1_seed == 1 else 'nd' if team1_seed == 2 else 'rd' if team1_seed == 3 else 'th' if isinstance(team1_seed, int) else ''})</div>
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
                                <div style="font-size: 13px; color: #666; margin-top: 2px;">({team2['league_name']}, {team2['wins']}-{team2['losses']}, {team2_seed}{'st' if team2_seed == 1 else 'nd' if team2_seed == 2 else 'rd' if team2_seed == 3 else 'th' if isinstance(team2_seed, int) else ''})</div>
                            </div>
                        </div>
                        <div style="font-size: 32px; font-weight: bold; color: {'#3eab43' if team2_winning else '#666'};">
                            {team2_score if team2_score is not None else '---'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("")
