import math

from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.templates import templates
from backend.app.db.database import get_db
from backend.app.crud.word import get_words_paginated


router = APIRouter()


@router.get("/words")
def words_page(
    request: Request,
    page: int = Query(1, ge=1),
    keyword: str = "",
    sort: str = "latest",
    db: Session = Depends(get_db)
):
    per_page = 20

    words, total_count = get_words_paginated(
        db=db,
        page=page,
        per_page=per_page,
        keyword=keyword,
        sort=sort
    )

    total_pages = math.ceil(total_count / per_page)

    if total_pages == 0:
        total_pages = 1

    return templates.TemplateResponse(
        request=request,
        name="words.html",
        context={
            "words": words,
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
            "total_pages": total_pages,
            "keyword": keyword,
            "sort": sort
        }
    )