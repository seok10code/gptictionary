from sqlalchemy.orm import Session

from backend.app.models.word import Word
from backend.app.schemas.word import WordCreate, WordUpdate


def get_words(db: Session):
    return db.query(Word).all()


def get_word_by_id(db: Session, word_id: int):
    return db.query(Word).filter(Word.id == word_id).first()


def get_word_by_vocabulary(db: Session, vocabulary: str):
    return db.query(Word).filter(Word.vocabulary == vocabulary).first()


def search_words(db: Session, keyword: str):
    return (
        db.query(Word)
        .filter(Word.vocabulary.like(f"%{keyword}%"))
        .all()
    )


def get_words_paginated(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    keyword: str = "",
    sort: str = "latest"
):
    query = db.query(Word)

    if keyword:
        query = query.filter(Word.vocabulary.like(f"%{keyword}%"))

    total_count = query.count()

    if sort == "abc":
        query = query.order_by(Word.vocabulary.asc())
    elif sort == "id":
        query = query.order_by(Word.id.asc())
    elif sort == "priority":
        query = query.order_by(Word.priority.desc())
    elif sort == "memorize":
        query = query.order_by(Word.memorize_count.desc())
    else:
        query = query.order_by(Word.id.desc())

    words = (
        query
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return words, total_count


def create_word(db: Session, word: WordCreate):
    db_word = Word(
        vocabulary=word.vocabulary,
        definition=word.definition,
        sentence=word.sentence,
        synonyms=word.synonyms,
        usage_note=word.usage_note
    )

    db.add(db_word)
    db.commit()
    db.refresh(db_word)

    return db_word


def update_word(db: Session, word_id: int, word: WordUpdate):
    db_word = db.query(Word).filter(Word.id == word_id).first()

    if not db_word:
        return None

    if word.vocabulary is not None:
        db_word.vocabulary = word.vocabulary

    if word.definition is not None:
        db_word.definition = word.definition

    if word.sentence is not None:
        db_word.sentence = word.sentence

    if word.synonyms is not None:
        db_word.synonyms = word.synonyms

    if word.usage_note is not None:
        db_word.usage_note = word.usage_note

    db.commit()
    db.refresh(db_word)

    return db_word


def delete_word(db: Session, word_id: int):
    db_word = db.query(Word).filter(Word.id == word_id).first()

    if not db_word:
        return None

    db.delete(db_word)
    db.commit()

    return db_word