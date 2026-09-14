from pydantic import BaseModel

from app.schemas.common import TeamRef


class StandingsRow(BaseModel):
    rank: int
    league_rank: int
    team: TeamRef
    wins: int
    losses: int
    points_for: float
    points_against: float
    transactions: int
    streak: str


class PlayoffStandingsRow(BaseModel):
    rank: int
    team: TeamRef
    wins: float
    losses: int
    points_for: float
    points_against: float
    streak: str
    gb: float
