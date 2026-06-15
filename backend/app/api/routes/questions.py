from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from backend.app.core.templates import templates
from backend.app.db.database import get_db
from backend.app.services.openai_service import ask_openai
from backend.app.services.embedding_service import create_embedding
from backend.app.services.qdrant_service import (
    save_question_to_qdrant,
    search_similar_questions,
)
from backend.app.services.db_query_service import (
    get_word_count,
    get_most_wrong_words,
    get_most_memorized_words,
)

router = APIRouter()


@router.get("/questions", response_class=HTMLResponse)
def questions_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="questions.html",
        context={
            "question": None,
            "answer": None,
            "similar_questions": [],
        },
    )


@router.post("/questions", response_class=HTMLResponse)
def ask_question(
    request: Request,
    question: str = Form(...),
    db: Session = Depends(get_db),
):
    question = question.strip()
    answer = None
    similar_questions = []

    try:
        if "몇 개" in question or "몇개" in question or "총" in question:
            count = get_word_count(db)
            answer = f"현재 단어장에는 총 {count}개의 단어가 저장되어 있어."

        elif "많이 틀린" in question or "제일 많이 틀린" in question:
            words = get_most_wrong_words(db, limit=10)
            answer = "가장 많이 틀린 단어 TOP 10:\n\n"
            for i, word in enumerate(words, 1):
                answer += f"{i}. {word.vocabulary} - 오답 {word.priority}회\n"

        elif "많이 외운" in question or "암기" in question:
            words = get_most_memorized_words(db, limit=10)
            answer = "가장 많이 외운 단어 TOP 10:\n\n"
            for i, word in enumerate(words, 1):
                answer += f"{i}. {word.vocabulary} - 정답 {word.memorize_count}회\n"

        else:
            vector = create_embedding(question)
            results = search_similar_questions(vector, limit=3)

            for r in results:
                if r.score >= 0.88:
                    similar_questions.append(
                        {
                            "score": round(r.score, 4),
                            "question": r.payload.get("question"),
                            "answer": r.payload.get("answer"),
                        }
                    )

            if similar_questions:
                answer = similar_questions[0]["answer"]
            else:
                answer = ask_openai(question)
                save_question_to_qdrant(
                    question=question,
                    answer=answer,
                    vector=vector,
                )

    except Exception as e:
        answer = f"에러 발생: {str(e)}"

    return templates.TemplateResponse(
        request=request,
        name="questions.html",
        context={
            "question": question,
            "answer": answer,
            "similar_questions": similar_questions,
        },
    )