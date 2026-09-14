from pydantic import BaseModel

from app.schemas.common import TeamRef


class RosterPlayer(BaseModel):
    player_id: str
    name: str
    position: str
    nfl_team: str
    nfl_logo: str
    positional_rank: str
    sort_order: int


class TeamSummary(BaseModel):
    team: TeamRef
    wins: int
    losses: int


class TeamDetail(BaseModel):
    team: TeamRef
    wins: int
    losses: int
    seed: str
    logo: str
    roster: list[RosterPlayer]


class ScheduleGame(BaseModel):
    week: int
    opponent: TeamRef
    opponent_logo: str
    location: str
    result: str
    result_color: str
    team_score: float | None
    opp_score: float | None
    is_current: bool
    game_type: str
