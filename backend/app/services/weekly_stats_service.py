from sqlalchemy.orm import Session

from app.core.constants import LEAGUES
from app.db.models import Matchup, MatchupParticipant
from app.services import standings_service
from app.services.espn_client import get_matchup_roster_details, get_team_logo
from app.services.standings_service import get_team_score_for_week


def _get_participant_roster(participant: MatchupParticipant, week: int) -> list[dict]:
    for m in get_matchup_roster_details(participant.league_id, week):
        if m["home_team"]["id"] == participant.team_id:
            return m["home_team"]["roster"]
        if m["away_team"]["id"] == participant.team_id:
            return m["away_team"]["roster"]
    return []


def build_regular_season_pairs(week: int) -> list[dict]:
    pairs = []
    for league_name, league_id in LEAGUES.items():
        for m in get_matchup_roster_details(league_id, week):
            home, away = m["home_team"], m["away_team"]
            pairs.append(
                {
                    "team1": {
                        "team": standings_service.team_ref(league_id, league_name, home["id"], home["name"]),
                        "score": home["total_points"],
                        "logo": home["logo"],
                        "roster": home["roster"],
                    },
                    "team2": {
                        "team": standings_service.team_ref(league_id, league_name, away["id"], away["name"]),
                        "score": away["total_points"],
                        "logo": away["logo"],
                        "roster": away["roster"],
                    },
                }
            )
    return pairs


def build_playoff_pairs(db: Session, season: int, week: int) -> list[dict]:
    pairs = []
    for matchup in db.query(Matchup).filter(Matchup.season == season, Matchup.week == week).all():
        home_p = next(p for p in matchup.participants if p.side == "home")
        away_p = next(p for p in matchup.participants if p.side == "away")

        home_score = get_team_score_for_week(home_p.league_id, home_p.team_name, week) or 0
        away_score = get_team_score_for_week(away_p.league_id, away_p.team_name, week) or 0

        pairs.append(
            {
                "team1": {
                    "team": standings_service.team_ref(home_p.league_id, home_p.league_name, home_p.team_id, home_p.team_name),
                    "score": home_score,
                    "logo": get_team_logo(home_p.league_id, home_p.team_id),
                    "roster": _get_participant_roster(home_p, week),
                },
                "team2": {
                    "team": standings_service.team_ref(away_p.league_id, away_p.league_name, away_p.team_id, away_p.team_name),
                    "score": away_score,
                    "logo": get_team_logo(away_p.league_id, away_p.team_id),
                    "roster": _get_participant_roster(away_p, week),
                },
            }
        )
    return pairs


def calculate_weekly_stats(week: int, matchup_pairs: list[dict]) -> dict:
    all_players: list[dict] = []
    all_team_scores: list[dict] = []
    league_order: list[str] = []

    for mp in matchup_pairs:
        for side in (mp["team1"], mp["team2"]):
            league_name = side["team"]["league_name"]
            if league_name not in league_order:
                league_order.append(league_name)

        t1, t2 = mp["team1"], mp["team2"]
        all_team_scores.append(
            {"team": t1["team"], "league": t1["team"]["league_name"], "score": t1["score"], "logo": t1.get("logo", ""),
             "opponent": t2["team"]["team_name"], "opponent_score": t2["score"]}
        )
        all_team_scores.append(
            {"team": t2["team"], "league": t2["team"]["league_name"], "score": t2["score"], "logo": t2.get("logo", ""),
             "opponent": t1["team"]["team_name"], "opponent_score": t1["score"]}
        )

        for side in (t1, t2):
            for player in side.get("roster", []):
                all_players.append(
                    {
                        "name": player["name"],
                        "nfl_team": player["nfl_team"],
                        "position": player["position"],
                        "points": player["points"],
                        "player_id": player.get("player_id", ""),
                        "team_name": side["team"]["team_name"],
                        "team_logo": side.get("logo", ""),
                    }
                )

    # 1. Top performers (dedupe a player appearing on multiple fantasy rosters)
    player_dict: dict[str, dict] = {}
    for p in all_players:
        entry = player_dict.setdefault(
            p["name"],
            {
                "name": p["name"],
                "nfl_team": p["nfl_team"],
                "position": p["position"],
                "points": p["points"],
                "player_id": p["player_id"],
                "teams": [],
                "team_logos": [],
            },
        )
        if p["team_name"] not in entry["teams"]:
            entry["teams"].append(p["team_name"])
            entry["team_logos"].append(p["team_logo"])
    top_performers = sorted(player_dict.values(), key=lambda x: x["points"], reverse=True)[:5]

    # 2. Weekly league leaders
    league_leaders = []
    for league_name in league_order:
        league_teams = [t for t in all_team_scores if t["league"] == league_name]
        if not league_teams:
            continue
        top_team = max(league_teams, key=lambda x: x["score"])
        league_leaders.append(
            {"league_name": league_name, "team": top_team["team"], "logo": top_team["logo"], "score": top_team["score"]}
        )

    # 3. Close games (margin <= 3), deduped per pair
    close_games = []
    seen_close: set[tuple[str, str]] = set()
    for t in all_team_scores:
        if t["score"] <= 0:
            continue
        margin = abs(t["score"] - t["opponent_score"])
        if margin > 3:
            continue
        pair_key = tuple(sorted([t["team"]["team_name"], t["opponent"]]))
        if pair_key in seen_close:
            continue
        seen_close.add(pair_key)
        close_games.append(
            {
                "league_name": t["league"],
                "team_a": t["team"]["team_name"],
                "team_b": t["opponent"],
                "score_a": t["score"],
                "score_b": t["opponent_score"],
                "margin": round(margin, 1),
            }
        )

    # 4. Biggest blowouts (top 3 by margin), deduped per pair
    blowout_candidates = []
    seen_blowout: set[tuple[str, str]] = set()
    for t in all_team_scores:
        if t["score"] <= 0:
            continue
        pair_key = tuple(sorted([t["team"]["team_name"], t["opponent"]]))
        if pair_key in seen_blowout:
            continue
        seen_blowout.add(pair_key)
        margin = abs(t["score"] - t["opponent_score"])
        if t["score"] > t["opponent_score"]:
            winner, winner_score = t["team"]["team_name"], t["score"]
            loser, loser_score = t["opponent"], t["opponent_score"]
        else:
            winner, winner_score = t["opponent"], t["opponent_score"]
            loser, loser_score = t["team"]["team_name"], t["score"]
        blowout_candidates.append(
            {
                "league_name": t["league"],
                "winner": winner,
                "winner_score": winner_score,
                "loser": loser,
                "loser_score": loser_score,
                "margin": round(margin, 1),
            }
        )
    blowouts = sorted(blowout_candidates, key=lambda x: x["margin"], reverse=True)[:3]

    # 5. Summary
    if all_team_scores:
        total_points = round(sum(t["score"] for t in all_team_scores), 1)
        avg_points = round(total_points / len(all_team_scores), 1)
        league_totals = {
            league_name: round(sum(t["score"] for t in all_team_scores if t["league"] == league_name), 1)
            for league_name in league_order
            if any(t["league"] == league_name for t in all_team_scores)
        }
        highest = max(league_totals.items(), key=lambda x: x[1]) if league_totals else (None, 0)
        lowest = min(league_totals.items(), key=lambda x: x[1]) if league_totals else (None, 0)
        summary = {
            "total_points": total_points,
            "average_points": avg_points,
            "highest_scoring_league": highest[0],
            "highest_scoring_league_points": highest[1],
            "lowest_scoring_league": lowest[0],
            "lowest_scoring_league_points": lowest[1],
        }
    else:
        summary = {
            "total_points": 0,
            "average_points": 0,
            "highest_scoring_league": None,
            "highest_scoring_league_points": 0,
            "lowest_scoring_league": None,
            "lowest_scoring_league_points": 0,
        }

    return {
        "week": week,
        "top_performers": top_performers,
        "league_leaders": league_leaders,
        "close_games": close_games,
        "blowouts": blowouts,
        "summary": summary,
    }
