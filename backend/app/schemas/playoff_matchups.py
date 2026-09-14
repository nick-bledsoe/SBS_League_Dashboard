from pydantic import BaseModel

from app.schemas.common import TeamRef


class ParticipantInput(BaseModel):
    league_id: str
    league_name: str
    team_id: int
    team_name: str


class PlayoffMatchupCreate(BaseModel):
    season: int
    week: int
    round_type: str
    home: ParticipantInput
    away: ParticipantInput


class PlayoffMatchupUpdate(BaseModel):
    round_type: str


class ParticipantRead(BaseModel):
    team: TeamRef
    wins: float
    losses: int
    seed: str
    score: float | None
    logo: str
    winning: bool


class PlayoffMatchupRead(BaseModel):
    id: int
    season: int
    week: int
    round_type: str
    home: ParticipantRead
    away: ParticipantRead
