"""Main FastAPI application."""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path

from app.config import settings
from app.db import get_db, init_db
from app.models import Document, Chunk, QueryHistory
from app.pdf_utils import PDFProcessor
from app.embedding import EmbeddingGenerator
from app.retriever import VectorRetriever

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pdf_processor = PDFProcessor(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP
)
embedding_generator = EmbeddingGenerator(settings.EMBEDDING_MODEL)
retriever = VectorRetriever(embedding_generator)

# Ensure uploads directory exists
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    # Try to load existing vector store
    try:
        retriever.load()
    except:
        pass


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Research Assistant API", "version": settings.API_VERSION}


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a PDF document."""
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save uploaded file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Check file size
    file_size = file_path.stat().st_size
    max_size = settings.MAX_PDF_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        file_path.unlink()
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum of {settings.MAX_PDF_SIZE_MB}MB"
        )
    
    try:
        # Process PDF
        result = pdf_processor.process_pdf(str(file_path))
        chunks = result['chunks']
        metadata = result['metadata']
        
        # Save document to database
        db_document = Document(
            filename=file.filename,
            file_path=str(file_path),
            title=metadata.get('title'),
            author=metadata.get('author'),
            pages=metadata.get('pages'),
            file_size=file_size
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Save chunks to database
        for chunk_data in chunks:
            db_chunk = Chunk(
                document_id=db_document.id,
                chunk_index=chunk_data['chunk_index'],
                content=chunk_data['content'],
                page_number=chunk_data.get('page_number'),
                start_char=chunk_data.get('start_char'),
                end_char=chunk_data.get('end_char')
            )
            db.add(db_chunk)
        
        db.commit()
        
        # Add chunks to vector store
        retriever.add_chunks(chunks)
        retriever.save()
        
        return {
            "message": "Document uploaded and processed successfully",
            "document_id": db_document.id,
            "filename": file.filename,
            "chunks": len(chunks),
            "metadata": metadata
        }
    
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.get("/api/documents")
async def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents."""
    documents = db.query(Document).all()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "title": doc.title,
            "author": doc.author,
            "pages": doc.pages,
            "upload_date": doc.upload_date.isoformat() if doc.upload_date else None,
            "file_size": doc.file_size
        }
        for doc in documents
    ]


@app.get("/api/documents/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document by ID."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "filename": document.filename,
        "title": document.title,
        "author": document.author,
        "pages": document.pages,
        "upload_date": document.upload_date.isoformat() if document.upload_date else None,
        "file_size": document.file_size
    }


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and its chunks."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete chunks
    db.query(Chunk).filter(Chunk.document_id == document_id).delete()
    
    # Delete file
    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()
    
    # Delete document record
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}


@app.post("/api/query")
async def query_documents(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results to return"),
    document_id: Optional[int] = Query(None, description="Filter by document ID"),
    db: Session = Depends(get_db)
):
    """Query documents and retrieve relevant chunks."""
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Search for relevant chunks
    results = retriever.search(query, top_k=top_k)
    
    # Filter by document_id if provided
    if document_id:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Filter chunks from the specified document
        doc_chunks = db.query(Chunk).filter(Chunk.document_id == document_id).all()
        chunk_contents = {chunk.content for chunk in doc_chunks}
        results = [r for r in results if r['content'] in chunk_contents]
    
    # Save query to database
    db_query = QueryHistory(
        query_text=query,
        document_id=document_id
    )
    db.add(db_query)
    db.commit()
    
    return {
        "query": query,
        "results": results,
        "count": len(results)
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

