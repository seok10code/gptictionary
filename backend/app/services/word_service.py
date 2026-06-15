import re
from sqlalchemy.orm import Session

from backend.app.crud.word import get_word_by_vocabulary, create_word
from backend.app.schemas.word import WordCreate
from backend.app.services.openai_service import generate_word_info


def is_valid_input(vocabulary: str) -> bool:
    if not vocabulary:
        return False

    if len(vocabulary) > 50:
        return False

    if not re.match(r"^[a-zA-Z\s\-']+$", vocabulary):
        return False

    return True


def search_word(db: Session, vocabulary: str):
    clean_vocabulary = vocabulary.strip().lower()

    if not is_valid_input(clean_vocabulary):
        return {
            "valid": False,
            "message": "올바른 영어 단어 또는 표현을 입력해주세요."
        }

    existing_word = get_word_by_vocabulary(
        db=db,
        vocabulary=clean_vocabulary
    )

    if existing_word:
        return {
            "valid": True,
            "word": existing_word,
            "source": "db"
        }

    ai_result = generate_word_info(clean_vocabulary)

    if not ai_result.get("valid"):
        return {
            "valid": False,
            "message": "유효한 영어 단어 또는 표현을 찾지 못했습니다."
        }

    word_create = WordCreate(
        vocabulary=clean_vocabulary,
        definition=ai_result.get("definition", ""),
        sentence=ai_result.get("sentence", ""),
        synonyms=ai_result.get("synonyms", ""),
        usage_note=ai_result.get("usage_note", "")
    )

    new_word = create_word(
        db=db,
        word=word_create
    )

    return {
        "valid": True,
        "word": new_word,
        "source": "openai"
    }