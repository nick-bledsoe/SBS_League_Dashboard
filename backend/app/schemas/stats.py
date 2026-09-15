from pydantic import BaseModel

from app.schemas.common import TeamRef


class TopPerformer(BaseModel):
    name: str
    nfl_team: str
    position: str
    points: float
    player_id: str
    teams: list[str]
    team_logos: list[str]


class LeagueLeader(BaseModel):
    league_name: str
    team: TeamRef
    logo: str
    score: float


class CloseGame(BaseModel):
    league_name: str
    team_a: str
    team_a_ref: TeamRef
    team_b: str
    team_b_ref: TeamRef
    score_a: float
    score_b: float
    margin: float


class Blowout(BaseModel):
    league_name: str
    winner: str
    winner_ref: TeamRef
    winner_score: float
    loser: str
    loser_ref: TeamRef
    loser_score: float
    margin: float


class WeeklySummary(BaseModel):
    total_points: float
    average_points: float
    highest_scoring_league: str | None
    highest_scoring_league_points: float
    lowest_scoring_league: str | None
    lowest_scoring_league_points: float


class WeeklyStats(BaseModel):
    week: int
    top_performers: list[TopPerformer]
    league_leaders: list[LeagueLeader]
    close_games: list[CloseGame]
    blowouts: list[Blowout]
    summary: WeeklySummary
