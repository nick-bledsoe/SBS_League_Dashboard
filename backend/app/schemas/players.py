from pydantic import BaseModel

from app.schemas.common import TeamRef


class PlayerNewsItem(BaseModel):
    id: int | None = None
    headline: str
    description: str
    story: str
    source: str
    published: str


class WeeklyPoints(BaseModel):
    week: int
    points: float


class StatSeasonRow(BaseModel):
    year: int | None
    team: str
    values: list[str]


class StatCategory(BaseModel):
    name: str
    display_name: str
    labels: list[str]
    seasons: list[StatSeasonRow]


class PlayerDetail(BaseModel):
    player_id: str
    name: str
    position: str
    nfl_team: str
    nfl_logo: str
    owners: list[TeamRef]
    weekly_points: list[WeeklyPoints]
    news: list[PlayerNewsItem]
    stats: list[StatCategory]


class PlayerRanking(BaseModel):
    player_id: str
    name: str
    position: str
    nfl_team: str
    league_id: str
    owners: list[TeamRef]
    total_points: float
    games_played: int
    avg_points: float
