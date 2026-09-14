from pydantic import BaseModel

from app.schemas.common import TeamRef


class BoxscorePlayer(BaseModel):
    player_id: str
    name: str
    position: str
    nfl_team: str
    points: float


class BoxscoreTeam(BaseModel):
    team: TeamRef
    logo: str
    total_points: float
    roster: list[BoxscorePlayer]


class BoxscoreMatchup(BaseModel):
    week: int
    home: BoxscoreTeam
    away: BoxscoreTeam


class RegularMatchup(BaseModel):
    league_name: str
    week: int
    home: TeamRef
    home_logo: str
    home_score: float
    away: TeamRef
    away_logo: str
    away_score: float
