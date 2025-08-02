import io
import hashlib
import requests
from typing import List, Tuple
from urllib.parse import urlparse
import PyPDF2
from docx import Document as DocxDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings


class DocumentProcessor:
    """Handles document downloading, text extraction, and chunking."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    async def download_document(self, url: str) -> Tuple[bytes, str]:
        """
        Download document from URL and return content with file extension.
        
        Args:
            url: Document URL
            
        Returns:
            Tuple of (document_content, file_extension)
            
        Raises:
            Exception: If download fails or file is too large
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Check file size
            content_length = len(response.content)
            max_size_bytes = settings.max_file_size_mb * 1024 * 1024
            
            if content_length > max_size_bytes:
                raise Exception(f"File too large: {content_length} bytes. Maximum allowed: {max_size_bytes} bytes")
            
            # Extract file extension from URL
            parsed_url = urlparse(url)
            file_extension = parsed_url.path.split('.')[-1].lower() if '.' in parsed_url.path else ''
            
            return response.content, file_extension
            
        except requests.RequestException as e:
            raise Exception(f"Failed to download document: {str(e)}")
    
    def extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF content."""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX content."""
        try:
            docx_file = io.BytesIO(content)
            doc = DocxDocument(docx_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")
    
    def extract_text_from_txt(self, content: bytes) -> str:
        """Extract text from TXT content."""
        try:
            # Try UTF-8 first, then fall back to other encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    continue
                    
            raise Exception("Could not decode text file with any supported encoding")
            
        except Exception as e:
            raise Exception(f"Failed to extract text from TXT: {str(e)}")
    
    async def process_document(self, url: str) -> Tuple[List[str], str]:
        """
        Download and process document into text chunks.
        
        Args:
            url: Document URL
            
        Returns:
            Tuple of (text_chunks, document_hash)
        """
        # Download document
        content, file_extension = await self.download_document(url)
        
        # Generate document hash for caching
        document_hash = hashlib.sha256(content).hexdigest()
        
        # Extract text based on file type
        if file_extension == 'pdf':
            text = self.extract_text_from_pdf(content)
        elif file_extension in ['docx', 'doc']:
            text = self.extract_text_from_docx(content)
        elif file_extension in ['txt', 'text']:
            text = self.extract_text_from_txt(content)
        else:
            raise Exception(f"Unsupported file type: {file_extension}")
        
        if not text.strip():
            raise Exception("No text content found in document")
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        if not chunks:
            raise Exception("Failed to create text chunks from document")
        
        return chunks, document_hash
    
    def get_document_hash(self, content: bytes) -> str:
        """Generate SHA256 hash for document content."""
        return hashlib.sha256(content).hexdigest()