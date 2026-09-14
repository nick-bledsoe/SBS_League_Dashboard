from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Matchup(Base):
    """A single matchup for a season/week. `phase` is "playoff" today; "regular" is reserved
    for a possible future full custom regular-season schedule feature."""

    __tablename__ = "matchups"
    __table_args__ = (Index("ix_matchups_season_week_phase", "season", "week", "phase"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    week: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    phase: Mapped[str] = mapped_column(String(20), nullable=False, default="playoff")
    round_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    participants: Mapped[list["MatchupParticipant"]] = relationship(
        back_populates="matchup", cascade="all, delete-orphan", lazy="joined"
    )


class MatchupParticipant(Base):
    """One side (home/away) of a Matchup. Only identity is stored here — record/seed/score
    are always joined live from the standings/playoff services at read time, since a
    snapshot taken at matchup-creation time would go stale as the season progresses."""

    __tablename__ = "matchup_participants"
    __table_args__ = (
        UniqueConstraint("matchup_id", "side", name="uq_matchup_side"),
        Index("ix_participants_league_team", "league_id", "team_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    matchup_id: Mapped[int] = mapped_column(
        ForeignKey("matchups.id", ondelete="CASCADE"), nullable=False
    )
    side: Mapped[str] = mapped_column(String(10), nullable=False)  # "home" | "away"
    league_id: Mapped[str] = mapped_column(String(20), nullable=False)
    league_name: Mapped[str] = mapped_column(String(50), nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, nullable=False)
    team_name: Mapped[str] = mapped_column(String(100), nullable=False)

    matchup: Mapped[Matchup] = relationship(back_populates="participants")
