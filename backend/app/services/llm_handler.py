from typing import List, Optional, Tuple
import google.generativeai as genai
from app.core.config import settings


class LLMHandler:
    """Handles language model interactions using Google Gemini."""
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # Configure generation settings
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.1,
            top_p=0.8,
            top_k=40,
            max_output_tokens=1024,
        )
    
    def _create_rag_prompt(self, question: str, context_chunks: List[str]) -> str:
        """
        Create a RAG prompt that forces the model to answer only from provided context.
        
        Args:
            question: User's question
            context_chunks: List of relevant text chunks
            
        Returns:
            Formatted prompt string
        """
        context_text = "\n\n".join([f"Context {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)])
        
        prompt = f"""You are an expert document analyst. Your task is to answer questions based STRICTLY on the provided context. Follow these rules:

1. ONLY use information that is explicitly stated in the provided context
2. If the context doesn't contain enough information to answer the question, say "I cannot answer this question based on the provided context."
3. Do not use any external knowledge or make assumptions
4. Be precise and cite specific parts of the context when possible
5. Keep your answer concise but comprehensive
6. If multiple contexts are relevant, synthesize the information clearly

CONTEXT:
{context_text}

QUESTION: {question}

ANSWER: Based on the provided context,"""
        
        return prompt
    
    async def get_answer(self, question: str, context_chunks: List[str]) -> Tuple[str, float]:
        """
        Generate an answer to the question using the provided context.
        
        Args:
            question: User's question
            context_chunks: List of relevant text chunks from the document
            
        Returns:
            Tuple of (answer, confidence_score)
        """
        try:
            if not context_chunks:
                return "I cannot answer this question as no relevant context was found.", 0.0
            
            # Create the RAG prompt
            prompt = self._create_rag_prompt(question, context_chunks)
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Extract the answer
            if response.text:
                answer = response.text.strip()
                
                # Calculate confidence based on response characteristics
                confidence = self._calculate_confidence(answer, context_chunks)
                
                return answer, confidence
            else:
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question.", 0.0
                
        except Exception as e:
            return f"An error occurred while generating the answer: {str(e)}", 0.0
    
    def _calculate_confidence(self, answer: str, context_chunks: List[str]) -> float:
        """
        Calculate a confidence score based on the answer and context.
        
        Args:
            answer: Generated answer
            context_chunks: Context used for generation
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        try:
            # Basic confidence calculation based on answer characteristics
            confidence = 0.5  # Base confidence
            
            # Check if the answer indicates uncertainty
            uncertainty_phrases = [
                "cannot answer",
                "not clear",
                "unclear",
                "insufficient information",
                "not enough context",
                "don't know",
                "unsure"
            ]
            
            answer_lower = answer.lower()
            
            # Reduce confidence if uncertainty phrases are present
            for phrase in uncertainty_phrases:
                if phrase in answer_lower:
                    confidence = max(0.1, confidence - 0.3)
                    break
            
            # Increase confidence if answer seems comprehensive
            if len(answer) > 100 and any(chunk.lower() in answer_lower for chunk in context_chunks):
                confidence = min(1.0, confidence + 0.2)
            
            # Check if answer references context
            if any(word in answer_lower for word in ["according to", "the document states", "based on"]):
                confidence = min(1.0, confidence + 0.1)
            
            # Ensure confidence is within valid range
            return max(0.0, min(1.0, confidence))
            
        except Exception:
            return 0.5  # Default confidence if calculation fails
    
    async def get_answer_with_sources(
        self, 
        question: str, 
        context_chunks: List[str]
    ) -> Tuple[str, List[str], float]:
        """
        Generate an answer with explicit source tracking.
        
        Args:
            question: User's question
            context_chunks: List of relevant text chunks
            
        Returns:
            Tuple of (answer, sources_used, confidence_score)
        """
        answer, confidence = await self.get_answer(question, context_chunks)
        
        # Identify which sources were likely used
        sources_used = []
        answer_lower = answer.lower()
        
        for chunk in context_chunks:
            # Check if any significant words from the chunk appear in the answer
            chunk_words = set(chunk.lower().split())
            answer_words = set(answer_lower.split())
            
            # Calculate overlap
            overlap = len(chunk_words.intersection(answer_words))
            if overlap > 3:  # Threshold for considering a source as used
                # Truncate chunk for display
                display_chunk = chunk[:200] + "..." if len(chunk) > 200 else chunk
                sources_used.append(display_chunk)
        
        # If no sources identified, use the first few chunks as fallback
        if not sources_used and context_chunks:
            sources_used = [chunk[:200] + "..." if len(chunk) > 200 else chunk 
                           for chunk in context_chunks[:2]]
        
        return answer, sources_used, confidence