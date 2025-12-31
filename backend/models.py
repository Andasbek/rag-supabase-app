from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class SourceResponse(BaseModel):
    id: uuid.UUID
    filename: str
    status: str
    created_at: datetime
    error: Optional[str] = None

class ChatRequest(BaseModel):
    question: str
    source_ids: Optional[List[uuid.UUID]] = None

class Source(BaseModel):
    source_id: uuid.UUID
    filename: str
    chunk_index: int
    similarity: float
    chunk_text: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
