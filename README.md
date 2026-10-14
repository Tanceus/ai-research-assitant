# AI Research Assistant

An AI-powered research assistant that allows you to upload PDF documents and query them using semantic search powered by embeddings and vector similarity.

## Features

- 📄 **PDF Upload**: Upload and process PDF research papers
- 🔍 **Semantic Search**: Query documents using natural language
- 🧠 **AI-Powered**: Uses sentence transformers for embeddings and vector similarity search
- 💾 **Persistent Storage**: PostgreSQL database for document metadata and chunks
- 🎨 **Modern UI**: Clean, responsive React frontend
- 🐳 **Docker Support**: Easy deployment with Docker Compose

## Architecture

### Backend (FastAPI)
- **PDF Processing**: Extracts text from PDFs using PyPDF2 and pdfplumber
- **Embeddings**: Generates embeddings using sentence-transformers
- **Vector Search**: FAISS for efficient similarity search
- **Database**: PostgreSQL for storing documents and chunks

### Frontend (React)
- Modern React application with Vite
- Upload and manage documents
- Query interface with results display

## Prerequisites

- Docker and Docker Compose
- Or Python 3.11+ and Node.js 18+ for local development

## Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-research-assistant
```

2. Start all services:
```bash
docker-compose up --build
```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Local Development

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (create `.env` file):
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/research_assistant
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_STORE_PATH=./vector_store
```

5. Start PostgreSQL database (or use Docker):
```bash
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=research_assistant -p 5432:5432 postgres:15-alpine
```

6. Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

## Usage

1. **Upload a PDF**: Click "Choose PDF File" and select a research paper PDF
2. **View Documents**: See all uploaded documents in the documents list
3. **Query Documents**: Enter a question in the query box and click "Search"
4. **Filter by Document**: Click on a document card to filter queries to that document only
5. **Delete Documents**: Click the × button on a document card to delete it

## API Endpoints

- `GET /` - API root
- `POST /api/documents/upload` - Upload a PDF document
- `GET /api/documents` - List all documents
- `GET /api/documents/{id}` - Get a specific document
- `DELETE /api/documents/{id}` - Delete a document
- `POST /api/query` - Query documents (query params: `query`, `top_k`, `document_id`)
- `GET /api/health` - Health check

## Configuration

Environment variables can be set in a `.env` file or through Docker environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `EMBEDDING_MODEL`: Sentence transformer model name
- `VECTOR_STORE_PATH`: Path to store vector indices
- `MAX_PDF_SIZE_MB`: Maximum PDF file size (default: 50MB)
- `CHUNK_SIZE`: Text chunk size for embeddings (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)

## Project Structure

```
ai-research-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── config.py        # Configuration settings
│   │   ├── db.py            # Database connection
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── pdf_utils.py     # PDF processing utilities
│   │   ├── embedding.py     # Embedding generation
│   │   ├── retriever.py     # Vector retrieval system
│   │   └── __init__.py
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── App.css          # Styles
│   │   ├── api.js           # API client
│   │   └── main.jsx         # React entry point
│   ├── package.json         # Node dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── index.html           # HTML template
│   └── Dockerfile           # Frontend Dockerfile
├── demo_pdfs/               # Sample PDF files
├── docker-compose.yml       # Docker Compose configuration
└── README.md                # This file
```

## Technologies Used

### Backend
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM for database operations
- PostgreSQL - Relational database
- PyPDF2 / pdfplumber - PDF processing
- sentence-transformers - Embedding generation
- FAISS - Vector similarity search

### Frontend
- React - UI library
- Vite - Build tool and dev server

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

