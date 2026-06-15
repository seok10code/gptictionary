from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func

from backend.app.db.database import Base


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)

    word_id = Column(
        Integer,
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False
    )

    question = Column(Text, nullable=False)
    answer = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)

    correct_count = Column(Integer, default=0)
    wrong_count = Column(Integer, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )