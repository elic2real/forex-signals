from fastapi import APIRouter
from ..models import JournalEntry

router = APIRouter()

@router.get("/journal", response_model=JournalEntry)
def get_journal_entry():
    # TODO: Return journal entry
    return JournalEntry(
        entry="Sample journal entry",
        context={},
        timestamp=0
    )
