from sqlalchemy.orm import Session
from backend.app.models.word import Word


def get_word_count(db: Session) -> int:
    return db.query(Word).count()


def get_most_wrong_words(db: Session, limit: int = 10):
    return (
        db.query(Word)
        .order_by(Word.priority.desc())
        .limit(limit)
        .all()
    )


def get_most_memorized_words(db: Session, limit: int = 10):
    return (
        db.query(Word)
        .order_by(Word.memorize_count.desc())
        .limit(limit)
        .all()
    )