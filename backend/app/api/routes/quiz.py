from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session

from backend.app.core.templates import templates
from backend.app.db.database import get_db
from backend.app.crud.quiz import (
    get_active_question,
    generate_quiz_question,
    generate_all_quiz_questions,
    submit_answer,
    make_hint,
)
from backend.app.models.word import Word


router = APIRouter()


def get_hint_for_question(db: Session, question):
    if not question:
        return None

    word = (
        db.query(Word)
        .filter(Word.id == question.word_id)
        .first()
    )

    if not word:
        return None

    return make_hint(word)


@router.get("/quiz")
def quiz_page(
    request: Request,
    db: Session = Depends(get_db)
):
    question = get_active_question(db)

    if not question:
        question = generate_quiz_question(db)

    hint = get_hint_for_question(db, question)

    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "question": question,
            "hint": hint,
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
            "hint": None,
            "result": result
        }
    )


@router.post("/quiz/generate-all")
def quiz_generate_all(
    db: Session = Depends(get_db)
):
    return generate_all_quiz_questions(db)