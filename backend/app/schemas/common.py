from pydantic import BaseModel


class TeamRef(BaseModel):
    league_id: str
    league_name: str
    team_id: int
    team_name: str
    owner: str = ""


class LeagueInfo(BaseModel):
    name: str
    id: str
