from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class Citation(BaseModel):
    source: str
    page_number: int
    chunk_number: Optional[int] = 0
    document_id: Optional[str] = ""


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    sources: Optional[List[Citation]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSummaryResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]

    class Config:
        from_attributes = True


class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Study Session"


class ChatRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[Citation] = []
