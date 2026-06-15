from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func

from backend.app.db.database import Base


class QuizLog(Base):
    __tablename__ = "quiz_logs"

    id = Column(Integer, primary_key=True, index=True)

    word_id = Column(
        Integer,
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False
    )

    question_id = Column(
        Integer,
        ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False
    )

    user_answer = Column(String(255))
    correct_answer = Column(String(255), nullable=False)

    is_correct = Column(Boolean, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )