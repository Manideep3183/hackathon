# Aura - Intelligent Document Query System

An enterprise-grade, full-stack web application that allows users to upload complex documents and ask natural language questions, powered by Google's Gemini AI models.

## 🚀 Features

- **Intelligent Document Processing**: Upload PDFs, DOCX, and TXT files for AI analysis
- **Natural Language Queries**: Ask questions in plain English about your documents
- **Accurate Answers with Sources**: Get precise answers with traceable source citations
- **Real-time Processing**: Fast document processing with progress indicators
- **Professional UI**: Clean, intuitive interface inspired by modern design standards
- **Enterprise Ready**: Production-grade architecture with PostgreSQL and vector search

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI**: High-performance async web framework
- **Google Gemini AI**: 
  - `gemini-1.5-pro-latest` for answer generation
  - `text-embedding-004` for document embeddings
- **Pinecone**: Vector database for semantic search
- **PostgreSQL**: Caching and query logging
- **Docker**: Containerized deployment

### Frontend (Next.js/TypeScript)
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Shadcn/UI**: Modern component library
- **TanStack Query**: Data fetching and caching

## 📋 Prerequisites

1. **Google Gemini API Key**
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. **Pinecone Account**
   - Sign up at [Pinecone](https://app.pinecone.io/)
   - Create a new index or use an existing one

3. **Docker & Docker Compose** (for containerized deployment)
   - [Install Docker](https://docs.docker.com/get-docker/)

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aura
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start PostgreSQL** (if not using Docker)
   ```bash
   # Using Docker for just PostgreSQL
   docker run -d \
     --name aura-postgres \
     -e POSTGRES_DB=aura_db \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=postgres123 \
     -p 5432:5432 \
     postgres:15-alpine
   ```

6. **Run the backend**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Google Gemini API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Pinecone Vector Database Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=aura-documents

# API Security
BEARER_TOKEN=your_secure_bearer_token_here
SECRET_KEY=your_secret_key_for_jwt_signing

# PostgreSQL Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password_here
POSTGRES_DB=aura_db
POSTGRES_PORT=5432

# Application Configuration
MAX_FILE_SIZE_MB=50
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

### API Authentication

The API uses bearer token authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer your_bearer_token_here
```

## 📡 API Documentation

### Main Endpoint

**POST** `/api/v1/hackrx/run`

Process a document and answer questions about it.

**Request Body:**
```json
{
  "document_url": "https://example.com/document.pdf",
  "questions": [
    {"question": "What is the main topic of this document?"},
    {"question": "What are the key findings?"}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "document_url": "https://example.com/document.pdf",
  "answers": [
    {
      "question": "What is the main topic of this document?",
      "answer": "The document discusses...",
      "sources": ["Source text chunks..."],
      "confidence": 0.92
    }
  ],
  "processing_time_ms": 2500
}
```

### Other Endpoints

- **GET** `/api/v1/health` - Health check
- **GET** `/api/v1/stats` - System statistics
- **GET** `/docs` - Interactive API documentation

## 🧠 How It Works

1. **Document Upload**: User provides a document URL
2. **Text Extraction**: System downloads and extracts text from the document
3. **Chunking**: Text is split into manageable chunks with overlap
4. **Embedding**: Chunks are converted to embeddings using Gemini's text-embedding-004
5. **Storage**: Embeddings are stored in Pinecone vector database
6. **Query Processing**: User questions are embedded and matched against document chunks
7. **Answer Generation**: Relevant chunks are sent to Gemini-1.5-pro for answer generation
8. **Response**: Structured answer with sources and confidence score is returned

## 🔒 Security Features

- Bearer token authentication
- Input validation and sanitization
- Rate limiting ready
- CORS configuration
- Secure Docker containers
- Non-root user execution

## 🎨 UI/UX Features

- Clean, professional design
- Responsive layout
- Real-time processing indicators
- Source citation display
- Confidence scoring
- Error handling with user-friendly messages
- Accessibility considerations

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📊 Monitoring

The application includes:
- Health check endpoints
- Processing time metrics
- Query logging to PostgreSQL
- Vector store statistics

## 🚀 Deployment

### Production Deployment

1. **Set production environment variables**
2. **Use production-grade PostgreSQL**
3. **Configure HTTPS/SSL**
4. **Set up reverse proxy (nginx)**
5. **Configure monitoring and logging**

### Scaling Considerations

- Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
- Configure Pinecone for production workloads
- Implement Redis for session management
- Use CDN for static assets
- Configure horizontal scaling with load balancers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Ensure all environment variables are correctly set
4. Verify API keys and network connectivity

## 🔮 Roadmap

- [ ] Support for more document formats (PowerPoint, Excel)
- [ ] Multi-language support
- [ ] Batch processing capabilities
- [ ] Advanced analytics dashboard
- [ ] Integration with cloud storage providers
- [ ] Mobile application
- [ ] Advanced user management
