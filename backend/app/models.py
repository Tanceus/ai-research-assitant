"""Database models."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from app.db import Base


class Document(Base):
    """Document model for storing PDF metadata."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    title = Column(String(500), nullable=True)
    author = Column(String(500), nullable=True)
    pages = Column(Integer, nullable=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    file_size = Column(Integer, nullable=True)  # in bytes


class Chunk(Base):
    """Chunk model for storing document chunks."""
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    start_char = Column(Integer, nullable=True)
    end_char = Column(Integer, nullable=True)


class QueryHistory(Base):
    """QueryHistory model for storing user queries and responses."""
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    document_id = Column(Integer, nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

