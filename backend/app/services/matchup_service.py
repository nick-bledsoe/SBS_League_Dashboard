from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import MATCHUP_TYPES
from app.core.errors import NotFoundError, ValidationError
from app.db.models import Matchup, MatchupParticipant
from app.schemas.playoff_matchups import ParticipantInput, PlayoffMatchupCreate
from app.services import standings_service
from app.services.espn_client import get_team_logo
from app.services.playoff_service import calculate_playoff_standings, get_ordinal
from app.services.standings_service import fetch_all_leagues, fetch_all_matchups, get_team_score_for_week


def _same_team(a: ParticipantInput, b: ParticipantInput) -> bool:
    return a.team_name == b.team_name and a.league_name == b.league_name


def create_matchup(db: Session, payload: PlayoffMatchupCreate, phase: str = "playoff") -> Matchup:
    if payload.round_type not in MATCHUP_TYPES:
        raise ValidationError(f"Invalid round_type. Must be one of: {', '.join(MATCHUP_TYPES)}")

    if _same_team(payload.home, payload.away):
        raise ValidationError("Cannot create a matchup with the same team on both sides")

    existing = (
        db.query(Matchup)
        .filter(Matchup.season == payload.season, Matchup.week == payload.week, Matchup.phase == phase)
        .all()
    )
    for matchup in existing:
        names = {(p.league_name, p.team_name) for p in matchup.participants}
        pair = {(payload.home.league_name, payload.home.team_name), (payload.away.league_name, payload.away.team_name)}
        if names == pair:
            raise ValidationError(f"This matchup already exists for week {payload.week}")

    matchup = Matchup(season=payload.season, week=payload.week, phase=phase, round_type=payload.round_type)
    matchup.participants = [
        MatchupParticipant(
            side="home",
            league_id=payload.home.league_id,
            league_name=payload.home.league_name,
            team_id=payload.home.team_id,
            team_name=payload.home.team_name,
        ),
        MatchupParticipant(
            side="away",
            league_id=payload.away.league_id,
            league_name=payload.away.league_name,
            team_id=payload.away.team_id,
            team_name=payload.away.team_name,
        ),
    ]
    db.add(matchup)
    db.commit()
    db.refresh(matchup)
    return matchup


def list_matchups(db: Session, season: int, week: int | None = None, phase: str = "playoff") -> list[Matchup]:
    stmt = select(Matchup).where(Matchup.season == season, Matchup.phase == phase)
    if week is not None:
        stmt = stmt.where(Matchup.week == week)
    return list(db.execute(stmt).unique().scalars().all())


def get_matchup(db: Session, matchup_id: int) -> Matchup:
    matchup = db.get(Matchup, matchup_id)
    if not matchup:
        raise NotFoundError(f"Matchup {matchup_id} not found")
    return matchup


def update_round_type(db: Session, matchup_id: int, round_type: str) -> Matchup:
    if round_type not in MATCHUP_TYPES:
        raise ValidationError(f"Invalid round_type. Must be one of: {', '.join(MATCHUP_TYPES)}")
    matchup = get_matchup(db, matchup_id)
    matchup.round_type = round_type
    db.commit()
    db.refresh(matchup)
    return matchup


def delete_matchup(db: Session, matchup_id: int) -> None:
    matchup = get_matchup(db, matchup_id)
    db.delete(matchup)
    db.commit()


def list_seasons_with_data(db: Session) -> list[int]:
    stmt = select(Matchup.season).distinct()
    return sorted({row[0] for row in db.execute(stmt).all()}, reverse=True)


def enrich_matchup(matchup: Matchup) -> dict:
    """Attach live record/seed/score/logo to a stored matchup's participants."""
    standings = fetch_all_leagues()
    matchups_for_week = fetch_all_matchups()
    playoff_standings = calculate_playoff_standings(standings, matchups_for_week)

    def enrich_side(p: MatchupParticipant) -> dict:
        record_row = next(
            (r for r in standings if r["team"]["team_name"] == p.team_name and r["team"]["league_name"] == p.league_name),
            None,
        )
        seed_row = next(
            (
                r
                for r in playoff_standings
                if r["team"]["team_name"] == p.team_name and r["team"]["league_name"] == p.league_name
            ),
            None,
        )
        score = get_team_score_for_week(p.league_id, p.team_name, matchup.week)
        return {
            "team": standings_service.team_ref(p.league_id, p.league_name, p.team_id, p.team_name),
            "wins": record_row["wins"] if record_row else 0,
            "losses": record_row["losses"] if record_row else 0,
            "seed": get_ordinal(seed_row["rank"]) if seed_row else "N/A",
            "score": score,
            "logo": get_team_logo(p.league_id, p.team_id),
            "winning": False,
        }

    home_p = next(p for p in matchup.participants if p.side == "home")
    away_p = next(p for p in matchup.participants if p.side == "away")
    home = enrich_side(home_p)
    away = enrich_side(away_p)

    if home["score"] is not None and away["score"] is not None:
        if home["score"] > away["score"]:
            home["winning"] = True
        elif away["score"] > home["score"]:
            away["winning"] = True

    return {
        "id": matchup.id,
        "season": matchup.season,
        "week": matchup.week,
        "round_type": matchup.round_type,
        "home": home,
        "away": away,
    }
