from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session

from backend.app.core.templates import templates
from backend.app.db.database import get_db
from backend.app.services.word_service import search_word


router = APIRouter()


@router.get("/search")
def search_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "query": "",
            "result": None,
            "error": None
        }
    )


@router.post("/search")
def search_submit(
    request: Request,
    query: str = Form(...),
    db: Session = Depends(get_db)
):
    result = search_word(
        db=db,
        vocabulary=query
    )

    if not result.get("valid"):
        return templates.TemplateResponse(
            request=request,
            name="search.html",
            context={
                "query": query,
                "result": None,
                "error": result.get("message")
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "query": query,
            "result": result.get("word"),
            "source": result.get("source"),
            "error": None
        }
    )