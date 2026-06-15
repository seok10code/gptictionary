from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from backend.app.db.database import Base


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)

    vocabulary = Column(String(255), nullable=False)
    definition = Column(Text, nullable=False)

    sentence = Column(Text)
    synonyms = Column(Text)
    usage_note = Column(Text)

    priority = Column(Integer, default=0)
    memorize_count = Column(Integer, default=0)

    total_correct = Column(Integer, default=0)
    total_wrong = Column(Integer, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )