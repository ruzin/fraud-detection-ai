from typing import Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum


class DocumentCategory(str, Enum):
    INVOICE = "invoice"
    MARKETPLACE_LISTING_SCREENSHOT = "marketplace_listing_screenshot"
    CHAT_SCREENSHOT = "chat_screenshot"
    WEBSITE_SCREENSHOT = "website_screenshot"
    OTHER = "other"


class ProcessingRequest(BaseModel):
    file_id: str
    filename: str
    content_type: str


class ProcessingResult(BaseModel):
    file_id: str
    filename: str
    category: DocumentCategory
    confidence: float
    extracted_content: Dict[str, Any]
    processing_time: float
    error: Optional[str] = None


class ExtractedContent(BaseModel):
    text: str
    key_entities: Dict[str, Any]
    dates: list
    metadata: Dict[str, Any]