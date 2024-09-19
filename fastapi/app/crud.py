from sqlalchemy.orm import Session
from . import models, schema
from sqlalchemy import and_, select, delete, func, text
from datetime import date


def get_cnt(db: Session, table_name: str):
    stmt = select(func.count()).select_from(text(table_name))  # 테이블 이름을 text()로 감싸줌
    result = db.execute(stmt)
    count = result.scalar_one()  # 결과를 스칼라 값으로 가져옴
    return count

# ###################################################################
def get_vocab(db: Session, vocab: str):
    return db.query(models.Vocab).filter(models.Vocab.vocabulary == vocab).first()

def get_vocabs_by_date(db: Session, sdate: str, edate: str):
    return db.query(models.Vocab).filter(
        and_(models.Vocab.db_load_dts >= sdate, models.Vocab.db_load_dts <= edate)
    ).all()

def get_vocabs(db: Session):
    return db.query(models.Vocab).all()

def create_vocab(db: Session, vocab: schema.VocabCreate):
    if vocab.db_load_dts is None:
        vocab.db_load_dts = date.today()  # 오늘 날짜로 기본값 설정
    db_vocab = models.Vocab(**vocab.dict())
    db.add(db_vocab)
    db.commit()
    db.refresh(db_vocab)
    return db_vocab

def update_vocab(db: Session, vocab: models.Vocab, updated_vocab: schema.VocabCreate):
    for key, value in updated_vocab.dict().items():
        setattr(vocab, key, value)
    db.commit()
    db.refresh(vocab)
    return vocab

def delete_vocab(db: Session, vocab: models.Vocab):
    db.delete(vocab)
    db.commit()

def delete_all_vocabs(db: Session):
    db.query(models.Vocab).delete()
    db.commit()

############################ Checker ############################
def get_checker(db: Session, vocab_checker: str):
    return db.query(models.Checker).filter(models.Checker.vocabulary == vocab_checker).first()

def get_checker_by_priority(db: Session):
    checkers = (
        db.query(models.Checker)
        .filter(models.Checker.priority >= 0)  # priority가 1 이상인 것만 필터링
        .order_by(models.Checker.priority.desc())  # priority 기준으로 내림차순 정렬
        .all()
    )
    return [schema.Checker.from_orm(checker) for checker in checkers]

def get_all_checkers(db: Session):
    return db.query(models.Checker).all()

def create_vocab_checker(db: Session, checker: schema.CheckerCreate):
    if checker.db_load_dts is None:
        checker.db_load_dts = date.today().isoformat()  # 오늘 날짜로 기본값 설정
    db_checker = models.Checker(**checker.dict())
    db.add(db_checker)
    db.commit()
    db.refresh(db_checker)
    return db_checker

def update_checker(db: Session, checker: models.Checker, updated_checker: schema.CheckerCreate):
    for key, value in updated_checker.dict().items():
        setattr(checker, key, value)
    db.commit()
    db.refresh(checker)
    return checker

def delete_checker(db: Session, checker: models.Checker):
    db.delete(checker)
    db.commit()

def delete_checker_all(db: Session):
    stmt = delete(models.Checker)
    db.execute(stmt)
    db.commit()

def delete_checker_by_vocab(db: Session, vocab: str):
    stmt = delete(models.Checker).where(models.Checker.vocabulary == vocab)
    db.execute(stmt)
    db.commit()

###################Sentence######################
def get_sentences_with_pagination(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Sentences).offset(skip).limit(limit).all()

def get_sentences_by_frequency(db: Session):
    sentences = (
        db.query(models.Sentences)
        .order_by(models.Sentences.frequency.asc())  # frequency 기준 오름차순 정렬
        .limit(5)  # 5개만 가져옴
        .all()
    )
    return [schema.Sentence.from_orm(sentence) for sentence in sentences]

def get_all_sentences(db: Session):
    return db.query(models.Sentences).all()

def create_sentence(db: Session, sentence: schema.SentenceCreate):
    if sentence.db_load_dts is None:
        sentence.db_load_dts = date.today()  # 오늘 날짜로 기본값 설정
    db_sentence = models.Sentences(**sentence.dict())
    db.add(db_sentence)
    db.commit()
    db.refresh(db_sentence)
    return db_sentence

def get_sentence_by_id(db: Session, sentence_id: int):
    return db.query(models.Sentences).filter(models.Sentences.idx == sentence_id).first()

def update_sentence(db: Session, db_sentence: models.Sentences, updated_sentence: schema.SentenceCreate):
    for key, value in updated_sentence.dict().items():
        setattr(db_sentence, key, value)
    db.commit()
    db.refresh(db_sentence)
    return db_sentence

def delete_sentence(db: Session, db_sentence: models.Sentences):
    db.delete(db_sentence)
    db.commit()