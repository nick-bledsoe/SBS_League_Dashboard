from pydantic import BaseModel

from app.schemas.common import TeamRef


class TransactionPlayer(BaseModel):
    player_id: str
    name: str
    position: str
    nfl_team: str


class TransactionItem(BaseModel):
    action: str
    team: TeamRef
    player: TransactionPlayer


class TransactionEvent(BaseModel):
    id: str
    type: str
    week: int
    date: int
    items: list[TransactionItem]


class TransactionHighlight(BaseModel):
    player: TransactionPlayer
    count: int
    by: list[TeamRef]


class TransactionHighlights(BaseModel):
    week: int
    most_added: TransactionHighlight | None
    most_dropped: TransactionHighlight | None
