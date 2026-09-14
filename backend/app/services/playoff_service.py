"""Playoff seeding logic.

NOTE ON A BUG FOUND WHILE PORTING: the original `utils.calculate_playoff_standings`
(pandas version) computed a `playoff_teams` list implementing "each league's #1 auto-
qualifies, min 2 teams per league, fill to 8 by best record" -- but then built its
returned DataFrame from `all_teams` (the plain global sort) instead of `playoff_teams`.
That guarantee logic was dead code with no effect on the actual output, so the
Streamlit app's playoff picture was really just a plain global sort by (wins, points
for) with the +0.5 weekly-bonus applied -- despite the UI caption promising the
guarantees. This rewrite implements what the feature actually appears to intend
(matching the UI caption), locked in by tests in tests/test_playoff_standings.py.
"""

def get_ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _key(row: dict) -> tuple[str, str]:
    return (row["team"]["league_name"], row["team"]["team_name"])


def calculate_playoff_standings(
    standings: list[dict], matchups: list[dict] | None = None, playoff_size: int = 8
) -> list[dict]:
    """Rank all teams for the combined playoff picture.

    - Sorted by (wins desc, points_for desc).
    - The team with the single highest score across all leagues in `matchups` gets a
      +0.5 win bonus before sorting.
    - Each league's #1 team is guaranteed a top-`playoff_size` spot; every league is
      guaranteed at least 2 spots; remaining spots fill by best overall record.
    - `gb` (games back) is each team's win deficit versus the team in the last
      guaranteed playoff spot.
    """
    if not standings:
        return []

    teams = [dict(row, wins=float(row["wins"])) for row in standings]

    if matchups:
        performances = []
        for m in matchups:
            if m["home_score"] > 0:
                performances.append(
                    {"team_name": m["home"]["team_name"], "league_name": m["home"]["league_name"], "score": m["home_score"]}
                )
            if m["away_score"] > 0:
                performances.append(
                    {"team_name": m["away"]["team_name"], "league_name": m["away"]["league_name"], "score": m["away_score"]}
                )
        if performances:
            top = max(performances, key=lambda p: p["score"])
            for row in teams:
                if row["team"]["team_name"] == top["team_name"] and row["team"]["league_name"] == top["league_name"]:
                    row["wins"] += 0.5

    teams.sort(key=lambda row: (-row["wins"], -row["points_for"]))

    league_winners: dict[str, dict] = {}
    for row in teams:
        league = row["team"]["league_name"]
        if league not in league_winners:
            league_winners[league] = row

    guaranteed: list[dict] = list(league_winners.values())
    guaranteed_keys = {_key(row) for row in guaranteed}
    league_counts: dict[str, int] = {}
    for row in guaranteed:
        league = row["team"]["league_name"]
        league_counts[league] = league_counts.get(league, 0) + 1

    league_names = list(dict.fromkeys(row["team"]["league_name"] for row in teams))
    for league_name in league_names:
        if league_counts.get(league_name, 0) >= 2:
            continue
        for row in teams:
            if row["team"]["league_name"] != league_name or _key(row) in guaranteed_keys:
                continue
            guaranteed.append(row)
            guaranteed_keys.add(_key(row))
            league_counts[league_name] = league_counts.get(league_name, 0) + 1
            if league_counts[league_name] >= 2:
                break

    for row in teams:
        if len(guaranteed) >= playoff_size:
            break
        if _key(row) in guaranteed_keys:
            continue
        guaranteed.append(row)
        guaranteed_keys.add(_key(row))

    guaranteed.sort(key=lambda row: (-row["wins"], -row["points_for"]))
    remaining = [row for row in teams if _key(row) not in guaranteed_keys]

    final_order = guaranteed + remaining
    result = []
    for idx, row in enumerate(final_order, start=1):
        result.append(
            {
                "rank": idx,
                "team": row["team"],
                "wins": row["wins"],
                "losses": row["losses"],
                "points_for": round(row["points_for"], 1),
                "points_against": round(row["points_against"], 1),
                "streak": row["streak"],
                "gb": 0.0,
            }
        )

    cutoff_idx = min(playoff_size, len(result)) - 1
    cutoff_wins = result[cutoff_idx]["wins"] if result else 0.0
    for row in result:
        row["gb"] = round(row["wins"] - cutoff_wins, 1)

    return result
