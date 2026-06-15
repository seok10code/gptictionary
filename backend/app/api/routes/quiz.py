from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session

from backend.app.core.templates import templates
from backend.app.db.database import get_db
from backend.app.crud.quiz import (
    get_active_question,
    generate_quiz_question,
    submit_answer
)


router = APIRouter()


@router.get("/quiz")
def quiz_page(
    request: Request,
    db: Session = Depends(get_db)
):
    question = get_active_question(db)

    if not question:
        question = generate_quiz_question(db)

    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "question": question,
            "result": None
        }
    )


@router.post("/quiz")
def quiz_submit(
    request: Request,
    question_id: int = Form(...),
    user_answer: str = Form(...),
    db: Session = Depends(get_db)
):
    result = submit_answer(
        db=db,
        question_id=question_id,
        user_answer=user_answer
    )

    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "question": None,
            "result": result
        }
    )