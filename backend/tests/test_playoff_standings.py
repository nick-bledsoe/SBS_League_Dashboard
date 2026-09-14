from app.services.playoff_service import calculate_playoff_standings


def team(league, name, wins, points_for, losses=0, points_against=0, streak="-"):
    return {
        "team": {
            "league_id": league,
            "league_name": league,
            "team_id": hash(name) % 1000,
            "team_name": name,
            "owner": "",
        },
        "wins": wins,
        "losses": losses,
        "points_for": points_for,
        "points_against": points_against,
        "streak": streak,
    }


def find(result, name):
    return next(row for row in result if row["team"]["team_name"] == name)


def test_each_league_winner_auto_qualifies_even_with_worse_record():
    # League C's best team (C1, 4 wins) is worse on paper than several League A/B teams,
    # but must still be guaranteed a top-8 spot as C's #1.
    standings = [
        *[team("A", f"A{i}", wins=10 - i, points_for=100 - i) for i in range(6)],
        *[team("B", f"B{i}", wins=9 - i, points_for=90 - i) for i in range(6)],
        team("C", "C1", wins=4, points_for=40),
        team("C", "C2", wins=3, points_for=30),
    ]

    result = calculate_playoff_standings(standings)
    top8_names = {row["team"]["team_name"] for row in result[:8]}

    assert "C1" in top8_names


def test_league_gets_backfilled_to_minimum_two():
    standings = [
        *[team("A", f"A{i}", wins=10 - i, points_for=100 - i) for i in range(6)],
        *[team("B", f"B{i}", wins=9 - i, points_for=90 - i) for i in range(6)],
        team("C", "C1", wins=4, points_for=40),
        team("C", "C2", wins=3, points_for=30),
    ]

    result = calculate_playoff_standings(standings)
    top8_names = {row["team"]["team_name"] for row in result[:8]}

    assert "C1" in top8_names and "C2" in top8_names


def test_remaining_slots_fill_by_best_overall_record():
    # 3 leagues, each with 1 team -> 3 guaranteed winners, backfill can't add more
    # (no 2nd team per league), so the remaining 5 of 8 slots fill by pure record.
    standings = [
        team("A", "A1", wins=10, points_for=100),
        team("B", "B1", wins=9, points_for=90),
        team("C", "C1", wins=1, points_for=10),
        *[team("D", f"D{i}", wins=8 - i, points_for=80 - i) for i in range(6)],
    ]

    result = calculate_playoff_standings(standings)
    top8_names = [row["team"]["team_name"] for row in result[:8]]

    # Best 5 non-guaranteed teams by record (D0..D4) should fill out the remaining slots.
    for i in range(5):
        assert f"D{i}" in top8_names


def test_weekly_high_score_bonus_affects_ordering():
    standings = [
        team("A", "Leader", wins=5, points_for=100),
        team("A", "Challenger", wins=4.5, points_for=150),
        team("B", "Other", wins=3, points_for=80),
    ]
    matchups = [
        {
            "home": {"team_name": "Leader", "league_name": "A"},
            "home_score": 50,
            "away": {"team_name": "Other", "league_name": "B"},
            "away_score": 40,
        },
        {
            "home": {"team_name": "Challenger", "league_name": "A"},
            "home_score": 120,  # highest score of the week
            "away": {"team_name": "Other", "league_name": "B"},
            "away_score": 30,
        },
    ]

    result = calculate_playoff_standings(standings, matchups)

    challenger = find(result, "Challenger")
    leader = find(result, "Leader")
    assert challenger["wins"] == 5.0  # 4.5 + 0.5 bonus
    assert challenger["rank"] < leader["rank"]  # bonus flips the tie


def test_two_team_league_does_not_break_backfill():
    standings = [
        team("A", "A1", wins=10, points_for=100),
        team("A", "A2", wins=9, points_for=90),
        *[team("B", f"B{i}", wins=8 - i, points_for=80 - i) for i in range(6)],
    ]

    # Should not raise, and both A teams should still be guaranteed (league has exactly 2).
    result = calculate_playoff_standings(standings)
    top8_names = {row["team"]["team_name"] for row in result[:8]}
    assert "A1" in top8_names and "A2" in top8_names


def test_gb_is_zero_for_last_guaranteed_playoff_team():
    standings = [team("A", f"A{i}", wins=10 - i, points_for=100 - i) for i in range(10)]
    result = calculate_playoff_standings(standings, playoff_size=8)
    assert result[7]["gb"] == 0.0
    assert result[8]["gb"] < 0
