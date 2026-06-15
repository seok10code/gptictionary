from datetime import datetime
from pydantic import BaseModel


class QuizQuestionBase(BaseModel):
    word_id: int
    question: str
    answer: str
    is_active: bool = True
    correct_count: int = 0
    wrong_count: int = 0


class QuizQuestionCreate(BaseModel):
    word_id: int
    question: str
    answer: str


class QuizQuestionRead(QuizQuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class QuizLogCreate(BaseModel):
    word_id: int
    question_id: int
    user_answer: str | None = None
    correct_answer: str
    is_correct: bool


class QuizLogRead(QuizLogCreate):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class QuizSubmit(BaseModel):
    question_id: int
    user_answer: str