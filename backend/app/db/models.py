from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class DocumentCache(Base):
    """Table for caching processed documents."""
    __tablename__ = "document_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    document_url = Column(String(2048), nullable=False, index=True)
    document_hash = Column(String(64), nullable=False, unique=True, index=True)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    chunk_count = Column(Integer, nullable=False)
    
    def __repr__(self):
        return f"<DocumentCache(url='{self.document_url}', hash='{self.document_hash[:8]}...')>"


class QueryLog(Base):
    """Table for logging queries and responses."""
    __tablename__ = "query_log"
    
    id = Column(Integer, primary_key=True, index=True)
    document_url = Column(String(2048), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON, nullable=False)  # List of source chunks
    processing_time_ms = Column(Integer, nullable=False)
    confidence_score = Column(String(10), nullable=True)  # Store as string to avoid float precision issues
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<QueryLog(question='{self.question[:50]}...', url='{self.document_url}')>"