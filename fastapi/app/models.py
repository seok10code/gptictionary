from sqlalchemy import Integer, String, Boolean, ForeignKey, DATE
from sqlalchemy.orm import mapped_column, relationship
from .database import Base

class Vocab(Base):
    __tablename__ = "vocab"
    vocabulary = mapped_column(String(50), primary_key=True)
    definition = mapped_column(String(1000), nullable=False)
    sentence = mapped_column(String(1000), nullable=False)
    synonyms = mapped_column(String(100), nullable=False)
    db_load_dts = mapped_column(DATE, nullable=False)  # TIMESTAMP에서 DATE로 변경
    
class Checker(Base):
    __tablename__="checker"
    vocabulary=mapped_column(String(50), primary_key=True)
    priority=mapped_column(Integer, nullable=False)
    problems=mapped_column(String(1000), nullable=False)
    memorize_count=mapped_column(Integer, nullable=False)
    db_load_dts = mapped_column(DATE, nullable=False)  # TIMESTAMP에서 DATE로 변경
    
class Sentences(Base):
    __tablename__ = "sentences"
    idx = mapped_column(Integer, primary_key=True, autoincrement=True)
    sentence = mapped_column(String(500), nullable=False)  # 문장 필드
    definition = mapped_column(String(1000), nullable=False)  # 문장의 뜻이나 해석 필드
    expression = mapped_column(String(1000), nullable=True)  # 추가 설명이나 예문 필드
    frequency=mapped_column(Integer, nullable=False)
    db_load_dts = mapped_column(DATE, nullable=False)