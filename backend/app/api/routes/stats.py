from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from backend.app.core.templates import templates
from backend.app.db.database import get_db
from backend.app.services.stats_service import (
    get_stats,
    get_top_wrong_words,
    get_top_memorized_words,
    get_recent_words,
    get_daily_added_words,
)

router = APIRouter()


@router.get("/stats", response_class=HTMLResponse)
def stats_page(
    request: Request,
    db: Session = Depends(get_db),
):
    wrong_words = get_top_wrong_words(db)
    memorized_words = get_top_memorized_words(db)
    recent_words = get_recent_words(db)
    daily_labels, daily_data = get_daily_added_words(db)

    return templates.TemplateResponse(
        request=request,
        name="stats.html",
        context={
            "stats": get_stats(db),
            "wrong_words": wrong_words,
            "memorized_words": memorized_words,
            "recent_words": recent_words,
            "wrong_chart_labels": [word.vocabulary for word in wrong_words],
            "wrong_chart_data": [word.priority for word in wrong_words],
            "memorized_chart_labels": [word.vocabulary for word in memorized_words],
            "memorized_chart_data": [word.memorize_count for word in memorized_words],
            "daily_labels": daily_labels,
            "daily_data": daily_data,
        },
    )