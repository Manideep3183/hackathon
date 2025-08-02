import uuid
from typing import List, Dict, Any
import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings


class VectorStoreManager:
    """Manages vector embeddings and retrieval using Google Gemini and Pinecone."""
    
    def __init__(self):
        # Initialize Google Gemini
        genai.configure(api_key=settings.google_api_key)
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = settings.pinecone_index_name
        self.embedding_dimension = 768  # text-embedding-004 dimension
        
        # Create index if it doesn't exist
        self._ensure_index_exists()
        
        # Get index instance
        self.index = self.pc.Index(self.index_name)
    
    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist."""
        try:
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='gcp',
                        region=settings.pinecone_environment
                    )
                )
        except Exception as e:
            print(f"Warning: Could not ensure index exists: {e}")
    
    def _generate_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
        """
        Generate embedding for text using Google Gemini.
        
        Args:
            text: Text to embed
            task_type: Task type for embedding (RETRIEVAL_DOCUMENT or RETRIEVAL_QUERY)
            
        Returns:
            List of embedding values
        """
        try:
            result = genai.embed_content(
                model='models/text-embedding-004',
                content=text,
                task_type=task_type
            )
            return result['embedding']
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    async def embed_and_upsert_chunks(
        self, 
        chunks: List[str], 
        document_url: str, 
        document_hash: str
    ) -> int:
        """
        Generate embeddings for text chunks and upsert to Pinecone.
        
        Args:
            chunks: List of text chunks
            document_url: Source document URL
            document_hash: Document hash for identification
            
        Returns:
            Number of chunks processed
        """
        try:
            vectors_to_upsert = []
            
            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self._generate_embedding(chunk, "RETRIEVAL_DOCUMENT")
                
                # Create unique ID for the chunk
                chunk_id = f"{document_hash}_{i}"
                
                # Prepare metadata
                metadata = {
                    "text": chunk,
                    "document_url": document_url,
                    "document_hash": document_hash,
                    "chunk_index": i,
                    "chunk_id": chunk_id
                }
                
                vectors_to_upsert.append({
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": metadata
                })
            
            # Upsert vectors in batches
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            return len(chunks)
            
        except Exception as e:
            raise Exception(f"Failed to embed and upsert chunks: {str(e)}")
    
    async def query_index(
        self, 
        query: str, 
        document_hash: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query the vector index for relevant chunks.
        
        Args:
            query: Query text
            document_hash: Document hash to filter results
            top_k: Number of top results to return
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query, "RETRIEVAL_QUERY")
            
            # Query the index
            query_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_values=False,
                include_metadata=True,
                filter={"document_hash": document_hash}
            )
            
            # Extract relevant chunks
            relevant_chunks = []
            for match in query_response.matches:
                chunk_data = {
                    "text": match.metadata.get("text", ""),
                    "score": match.score,
                    "chunk_index": match.metadata.get("chunk_index", 0),
                    "document_url": match.metadata.get("document_url", "")
                }
                relevant_chunks.append(chunk_data)
            
            return relevant_chunks
            
        except Exception as e:
            raise Exception(f"Failed to query index: {str(e)}")
    
    def delete_document_vectors(self, document_hash: str) -> bool:
        """
        Delete all vectors for a specific document.
        
        Args:
            document_hash: Document hash to delete
            
        Returns:
            True if successful
        """
        try:
            # Query for all vectors with the document hash
            query_response = self.index.query(
                vector=[0.0] * self.embedding_dimension,  # Dummy vector
                top_k=10000,  # Large number to get all matches
                include_values=False,
                include_metadata=True,
                filter={"document_hash": document_hash}
            )
            
            # Extract IDs to delete
            ids_to_delete = [match.id for match in query_response.matches]
            
            if ids_to_delete:
                self.index.delete(ids=ids_to_delete)
            
            return True
            
        except Exception as e:
            print(f"Warning: Failed to delete document vectors: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index."""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            return {"error": str(e)}