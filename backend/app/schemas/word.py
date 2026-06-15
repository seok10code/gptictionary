from datetime import datetime
from pydantic import BaseModel


class WordBase(BaseModel):
    vocabulary: str
    definition: str
    sentence: str | None = None
    synonyms: str | None = None
    usage_note: str | None = None


class WordCreate(WordBase):
    pass


class WordUpdate(BaseModel):
    vocabulary: str | None = None
    definition: str | None = None
    sentence: str | None = None
    synonyms: str | None = None
    usage_note: str | None = None


class WordRead(WordBase):
    id: int
    priority: int
    memorize_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }