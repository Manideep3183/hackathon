from typing import List, Optional, Any
from pydantic import BaseModel, HttpUrl, Field


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="The question to ask about the document")


class HackRXRequest(BaseModel):
    document_url: HttpUrl = Field(..., description="URL of the document to process")
    questions: List[QuestionRequest] = Field(..., min_items=1, max_items=10, description="List of questions to ask")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_url": "https://example.com/document.pdf",
                "questions": [
                    {"question": "What is the main topic of this document?"},
                    {"question": "What are the key findings mentioned?"}
                ]
            }
        }


class AnswerResponse(BaseModel):
    question: str = Field(..., description="The original question")
    answer: str = Field(..., description="The AI-generated answer")
    sources: List[str] = Field(default=[], description="Source chunks used to generate the answer")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score for the answer")


class HackRXResponse(BaseModel):
    success: bool = Field(..., description="Whether the request was successful")
    document_url: str = Field(..., description="The processed document URL")
    answers: List[AnswerResponse] = Field(..., description="List of answers to the questions")
    processing_time_ms: Optional[int] = Field(None, description="Total processing time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "document_url": "https://example.com/document.pdf",
                "answers": [
                    {
                        "question": "What is the main topic of this document?",
                        "answer": "The document discusses artificial intelligence and machine learning applications.",
                        "sources": [
                            "Artificial intelligence (AI) is transforming industries...",
                            "Machine learning algorithms enable computers to learn..."
                        ],
                        "confidence": 0.92
                    }
                ],
                "processing_time_ms": 2500
            }
        }


class ErrorResponse(BaseModel):
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")


# Database Models
class DocumentCache(BaseModel):
    id: Optional[int] = None
    document_url: str
    document_hash: str
    processed_at: Optional[str] = None
    chunk_count: int
    
    class Config:
        from_attributes = True


class QueryLog(BaseModel):
    id: Optional[int] = None
    document_url: str
    question: str
    answer: str
    sources: List[str]
    processing_time_ms: int
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True