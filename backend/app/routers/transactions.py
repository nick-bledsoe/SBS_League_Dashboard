from fastapi import APIRouter, Query

from app.schemas.transactions import TransactionEvent, TransactionHighlights
from app.services.transactions_service import get_week_transaction_highlights, get_week_transactions

router = APIRouter(tags=["transactions"])


@router.get("/weeks/{week}/transactions", response_model=list[TransactionEvent])
def week_transactions(week: int, league_id: str | None = Query(default=None)):
    return get_week_transactions(week, league_id)


@router.get("/weeks/{week}/transaction-highlights", response_model=TransactionHighlights)
def week_transaction_highlights(week: int):
    return get_week_transaction_highlights(week)
