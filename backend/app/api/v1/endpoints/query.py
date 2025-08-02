import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db.database import get_db
from app.db.models import DocumentCache, QueryLog
from app.models.schemas import HackRXRequest, HackRXResponse, AnswerResponse, ErrorResponse
from app.services.document_processor import DocumentProcessor
from app.services.vector_store_manager import VectorStoreManager
from app.services.llm_handler import LLMHandler

router = APIRouter()

# Initialize services
document_processor = DocumentProcessor()
vector_store_manager = VectorStoreManager()
llm_handler = LLMHandler()


@router.post("/hackrx/run", response_model=HackRXResponse)
async def process_document_and_answer_questions(
    request: HackRXRequest,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Main endpoint for processing documents and answering questions using Google Gemini.
    
    This endpoint:
    1. Downloads and processes the document
    2. Creates embeddings using Gemini text-embedding-004
    3. Stores vectors in Pinecone
    4. For each question, retrieves relevant context
    5. Generates answers using Gemini 1.5 Pro
    6. Returns structured responses with sources
    """
    start_time = time.time()
    document_url = str(request.document_url)
    
    try:
        # Step 1: Process the document
        print(f"Processing document: {document_url}")
        
        # Check if document is already cached
        existing_doc = db.query(DocumentCache).filter(
            DocumentCache.document_url == document_url
        ).first()
        
        if existing_doc:
            print(f"Using cached document with hash: {existing_doc.document_hash}")
            document_hash = existing_doc.document_hash
            chunks = []  # We'll retrieve from vector store if needed
        else:
            # Process new document
            chunks, document_hash = await document_processor.process_document(document_url)
            print(f"Document processed into {len(chunks)} chunks")
            
            # Step 2: Generate embeddings and store in Pinecone
            print("Generating embeddings and storing in Pinecone...")
            chunk_count = await vector_store_manager.embed_and_upsert_chunks(
                chunks, document_url, document_hash
            )
            
            # Cache the document in PostgreSQL
            doc_cache = DocumentCache(
                document_url=document_url,
                document_hash=document_hash,
                chunk_count=chunk_count
            )
            db.add(doc_cache)
            db.commit()
            print(f"Document cached with {chunk_count} chunks")
        
        # Step 3: Process questions
        answers = []
        
        for question_obj in request.questions:
            question = question_obj.question
            print(f"Processing question: {question}")
            
            # Step 4: Retrieve relevant context from Pinecone
            relevant_chunks = await vector_store_manager.query_index(
                query=question,
                document_hash=document_hash,
                top_k=5
            )
            
            if not relevant_chunks:
                # Fallback answer when no context found
                answer_response = AnswerResponse(
                    question=question,
                    answer="I cannot find relevant information in the document to answer this question.",
                    sources=[],
                    confidence=0.0
                )
            else:
                # Extract text chunks for LLM
                context_texts = [chunk["text"] for chunk in relevant_chunks]
                
                # Step 5: Generate answer using Gemini
                answer, sources, confidence = await llm_handler.get_answer_with_sources(
                    question=question,
                    context_chunks=context_texts
                )
                
                answer_response = AnswerResponse(
                    question=question,
                    answer=answer,
                    sources=sources,
                    confidence=confidence
                )
            
            answers.append(answer_response)
            
            # Log the query
            processing_time = int((time.time() - start_time) * 1000)
            query_log = QueryLog(
                document_url=document_url,
                question=question,
                answer=answer_response.answer,
                sources=answer_response.sources,
                processing_time_ms=processing_time,
                confidence_score=str(answer_response.confidence) if answer_response.confidence else None
            )
            db.add(query_log)
        
        # Commit all query logs
        db.commit()
        
        # Calculate total processing time
        total_processing_time = int((time.time() - start_time) * 1000)
        
        return HackRXResponse(
            success=True,
            document_url=document_url,
            answers=answers,
            processing_time_ms=total_processing_time
        )
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        db.rollback()
        
        # Return error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal server error",
                "details": str(e)
            }
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Aura Document Query API",
        "version": "1.0.0"
    }


@router.get("/stats")
async def get_stats(token: str = Depends(verify_token)):
    """Get system statistics."""
    try:
        vector_stats = vector_store_manager.get_index_stats()
        return {
            "vector_store": vector_stats,
            "status": "operational"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }