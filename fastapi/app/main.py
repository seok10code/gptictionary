from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal  # 동기 세션으로 변경
from . import crud, models, schema
from datetime import date
from typing import List

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=SessionLocal().get_bind())

app = FastAPI()

# Dependency Injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/ping")
def ping():
    return 'pong'

####################### Vocab #######################
@app.get("/vocab/count/{table_name}")
def get_vocab_cnt(table_name: str, db: Session = Depends(get_db)):
    cnt = crud.get_cnt(db, table_name)
    if not cnt:
        raise HTTPException(status_code=404, detail="No vocabs found")
    return cnt

@app.get("/vocab/all", response_model=list[schema.Vocab])
def get_vocabs(db: Session = Depends(get_db)):
    vocabs = crud.get_vocabs(db)
    if not vocabs:
        raise HTTPException(status_code=404, detail="No vocabs found")
    return vocabs

@app.get("/vocab/by_date/", response_model=list[schema.Vocab])
def get_vocabs_by_date(sdate: date, edate: date, db: Session = Depends(get_db)):
    vocabs = crud.get_vocabs_by_date(db, sdate=sdate, edate=edate)
    if not vocabs:
        raise HTTPException(status_code=404, detail="No vocabs found in the given date range")
    return vocabs

@app.get("/vocab/{vocabulary}/", response_model=schema.Vocab)
def get_vocab(vocabulary: str, db: Session = Depends(get_db)):
    db_vocab = crud.get_vocab(db, vocab=vocabulary)
    if db_vocab is None:
        raise HTTPException(status_code=404, detail="Vocab not found")
    return db_vocab

@app.post("/vocab/", response_model=schema.Vocab)
def post_vocab(vocab: schema.VocabCreate, db: Session = Depends(get_db)):
    # 중복 확인
    existing_vocab = crud.get_vocab(db, vocab.vocabulary)
    if existing_vocab:
        raise HTTPException(status_code=400, detail="Vocab already exists")
    return crud.create_vocab(db=db, vocab=vocab)

@app.put("/vocab/{vocabulary}/", response_model=schema.Vocab)
def update_vocab(vocabulary: str, updated_vocab: schema.VocabCreate, db: Session = Depends(get_db)):
    db_vocab = crud.get_vocab(db, vocab=vocabulary)
    if db_vocab is None:
        raise HTTPException(status_code=404, detail="Vocab not found")
    
    # vocabulary 필드가 변경되었는지 확인하고 중복 검사
    if updated_vocab.vocabulary != vocabulary:
        existing_vocab = crud.get_vocab(db, vocab=updated_vocab.vocabulary)
        if existing_vocab:
            raise HTTPException(status_code=400, detail="Vocab with this name already exists")
    
    return crud.update_vocab(db, db_vocab, updated_vocab)

@app.delete("/vocab/all/")
def delete_all_vocabs(db: Session = Depends(get_db)):
    try:
        crud.delete_all_vocabs(db)
        return {"message": "All vocabs deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting vocabs: {str(e)}")


@app.delete("/vocab/{vocabulary}/")
def delete_vocab(vocabulary: str, db: Session = Depends(get_db)):
    db_vocab = crud.get_vocab(db, vocab=vocabulary)
    if db_vocab is None:
        raise HTTPException(status_code=404, detail="Vocab not found")
    crud.delete_vocab(db, db_vocab)  # 여기에 전달되는 db_vocab이 올바른 Vocab 객체여야 합니다.
    return {"message": "Vocab deleted successfully"}

####################### Checker #######################
@app.get("/checkers/", response_model=list[schema.Checker])
def get_checkers(db: Session = Depends(get_db)):
    checkers = crud.get_all_checkers(db)
    if not checkers:
        raise HTTPException(status_code=404, detail="No checkers found")
    return checkers

@app.get("/checker/order/", response_model=List[schema.Checker])
def get_checker_by_priority(db: Session = Depends(get_db)):
    checkers = crud.get_checker_by_priority(db)
    if not checkers:
        raise HTTPException(status_code=404, detail="No checkers found")
    return checkers

@app.get("/checker/{vocab_checker}/", response_model=schema.Checker)
def get_checker(vocab_checker: str, db: Session = Depends(get_db)):
    db_checker = crud.get_checker(db, vocab_checker=vocab_checker)
    if db_checker is None:
        raise HTTPException(status_code=404, detail="Checker not found")
    return db_checker




@app.post("/checker/", response_model=schema.Checker)
def post_checker_for_vocab(checker: schema.CheckerCreate, db: Session = Depends(get_db)):
    existing_checker = crud.get_checker(db, vocab_checker=checker.vocabulary)
    if existing_checker:
        raise HTTPException(status_code=400, detail="Checker already exists for this vocab")
    return crud.create_vocab_checker(db=db, checker=checker)

@app.put("/checker/{vocab_checker}/", response_model=schema.Checker)
def update_checker(vocab_checker: str, updated_checker: schema.CheckerCreate, db: Session = Depends(get_db)):
    db_checker = crud.get_checker(db, vocab_checker=vocab_checker)
    if db_checker is None:
        raise HTTPException(status_code=404, detail="Checker not found")
    return crud.update_checker(db, db_checker, updated_checker)

@app.delete("/checker/all/")
def delete_checker_all(db: Session = Depends(get_db)):
    crud.delete_checker_all(db)
    return {"message": "All checkers deleted successfully"}

@app.delete("/checker/{vocab_checker}/")
def delete_checker(vocab_checker: str, db: Session = Depends(get_db)):
    db_checker = crud.get_checker(db, vocab_checker=vocab_checker)
    if db_checker is None:
        raise HTTPException(status_code=404, detail="Checker not found")
    crud.delete_checker(db, db_checker)
    return {"message": "Checker deleted successfully"}


###################Sentence######################
# 1. 모든 문장을 가져오는 엔드포인트 (skip, limit 적용)
@app.get("/sentences/", response_model=List[schema.Sentence])
def get_sentences(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    sentences = crud.get_sentences_with_pagination(db, skip=skip, limit=limit)
    if not sentences:
        raise HTTPException(status_code=404, detail="No sentences found")
    return sentences

@app.get("/sentences/frequency/", response_model=List[schema.Sentence])
def get_sentences_by_frequency(db: Session = Depends(get_db)):
    sentences = crud.get_sentences_by_frequency(db)
    if not sentences:
        raise HTTPException(status_code=404, detail="No sentences found")
    return sentences

# 2. 모든 문장을 가져오는 엔드포인트 (skip, limit 없이 전체)
@app.get("/sentences/all/", response_model=List[schema.Sentence])
def get_all_sentences(db: Session = Depends(get_db)):
    sentences = crud.get_all_sentences(db)
    if not sentences:
        raise HTTPException(status_code=404, detail="No sentences found")
    return sentences

@app.post("/sentence/", response_model=schema.Sentence)
def create_sentence(sentence: schema.SentenceCreate, db: Session = Depends(get_db)):
    if sentence.db_load_dts is None:
        sentence.db_load_dts = date.today()  # 현재 날짜로 기본값 설정
    return crud.create_sentence(db=db, sentence=sentence)

# 4. 문장을 업데이트하는 엔드포인트
@app.put("/sentence/{sentence_id}/", response_model=schema.Sentence)
def update_sentence(sentence_id: int, updated_sentence: schema.SentenceCreate, db: Session = Depends(get_db)):
    db_sentence = crud.get_sentence_by_id(db, sentence_id)
    if db_sentence is None:
        raise HTTPException(status_code=404, detail="Sentence not found")
    return crud.update_sentence(db, db_sentence, updated_sentence)

# 5. 문장을 삭제하는 엔드포인트
@app.delete("/sentence/{sentence_id}/")
def delete_sentence(sentence_id: int, db: Session = Depends(get_db)):
    db_sentence = crud.get_sentence_by_id(db, sentence_id)