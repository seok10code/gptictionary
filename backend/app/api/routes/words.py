import math

from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.templates import templates
from backend.app.db.database import get_db
from backend.app.crud.word import get_words_paginated
from backend.app.schemas.word import WordCreate
from backend.app.services.word_service import save_extracted_word


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


@router.post("/api/words/save")
def save_word(
    word: WordCreate,
    db: Session = Depends(get_db)
):
    return save_extracted_word(
        db=db,
        word=word
    )