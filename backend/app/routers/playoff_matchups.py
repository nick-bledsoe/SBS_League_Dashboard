from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import require_admin
from app.schemas.playoff_matchups import PlayoffMatchupCreate, PlayoffMatchupRead, PlayoffMatchupUpdate
from app.services import matchup_service

router = APIRouter(tags=["playoff-matchups"], dependencies=[Depends(require_admin)])


@router.post("/playoff-matchups", response_model=PlayoffMatchupRead, status_code=status.HTTP_201_CREATED)
def create_playoff_matchup(payload: PlayoffMatchupCreate, db: Session = Depends(get_db)):
    matchup = matchup_service.create_matchup(db, payload)
    return matchup_service.enrich_matchup(matchup)


@router.get("/playoff-matchups", response_model=list[PlayoffMatchupRead])
def list_playoff_matchups(season: int, week: int | None = Query(default=None), db: Session = Depends(get_db)):
    matchups = matchup_service.list_matchups(db, season, week)
    return [matchup_service.enrich_matchup(m) for m in matchups]


@router.patch("/playoff-matchups/{matchup_id}", response_model=PlayoffMatchupRead)
def update_playoff_matchup(matchup_id: int, payload: PlayoffMatchupUpdate, db: Session = Depends(get_db)):
    matchup = matchup_service.update_round_type(db, matchup_id, payload.round_type)
    return matchup_service.enrich_matchup(matchup)


@router.delete("/playoff-matchups/{matchup_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playoff_matchup(matchup_id: int, db: Session = Depends(get_db)):
    matchup_service.delete_matchup(db, matchup_id)
