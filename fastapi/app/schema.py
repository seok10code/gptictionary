from typing import Optional
from pydantic import BaseModel
from datetime import date

# Vocab Base Schema
class VocabBase(BaseModel):
    vocabulary: str
    definition: str
    sentence: str
    synonyms: str

# Vocab Create Schema (inherits from VocabBase)
class VocabCreate(VocabBase):
    db_load_dts: Optional[date] = None  # Date field specific to creation

# Vocab Schema (inherits from VocabBase)
class Vocab(VocabBase):
    db_load_dts: date  # Date field included in the full schema

    class Config:
        orm_mode = True
        from_attributes = True
# Checker Base Schema
class CheckerBase(BaseModel):
    vocabulary: str  # Foreign key reference to Vocab
    priority: int
    problems: str
    memorize_count: int

# Checker Create Schema (inherits from CheckerBase)
class CheckerCreate(CheckerBase):
    db_load_dts: Optional[date] = None  # Date field specific to creation

# Checker Schema (inherits from CheckerBase)
class Checker(CheckerBase):
    db_load_dts: date  # Date field included in the full schema

    class Config:
        orm_mode = True
        from_attributes = True

# Pydantic BaseModel 수정
class SentenceBase(BaseModel):
    sentence: str
    definition: str
    expression: Optional[str]  # nullable이므로 Optional로 지정
    frequency: int  # frequency 필드 추가

class SentenceCreate(SentenceBase):
    db_load_dts: date

class Sentence(SentenceBase):
    db_load_dts: date
    idx: Optional[int] = None  # 자동 생성되지 않는 경우 수동 생성 필요

    class Config:
        orm_mode = True
        from_attributes = True