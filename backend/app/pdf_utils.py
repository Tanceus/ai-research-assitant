"""PDF processing utilities."""
import os
import PyPDF2
from typing import List, Dict, Optional
from pathlib import Path
import pdfplumber


class PDFProcessor:
    """Handles PDF file processing and text extraction."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with text, metadata, and page information
        """
        text_by_page = []
        full_text = []
        metadata = {}
        
        try:
            # Extract metadata using PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = {
                    'pages': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', '') if pdf_reader.metadata else '',
                    'author': pdf_reader.metadata.get('/Author', '') if pdf_reader.metadata else '',
                }
            
            # Extract text using pdfplumber for better quality
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text() or ""
                    text_by_page.append({
                        'page_number': page_num,
                        'text': page_text
                    })
                    full_text.append(page_text)
            
            return {
                'full_text': '\n\n'.join(full_text),
                'text_by_page': text_by_page,
                'metadata': metadata
            }
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def chunk_text(self, text: str, page_number: Optional[int] = None) -> List[Dict[str, any]]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            page_number: Optional page number for tracking
            
        Returns:
            List of chunk dictionaries
        """
        if not text.strip():
            return []
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence or paragraph boundaries
            if end < len(text):
                # Look for sentence endings
                last_period = chunk_text.rfind('. ')
                last_newline = chunk_text.rfind('\n\n')
                break_point = max(last_period, last_newline)
                
                if break_point > self.chunk_size * 0.5:  # Only break if reasonable
                    chunk_text = text[start:start + break_point + 1]
                    end = start + break_point + 1
            
            chunks.append({
                'content': chunk_text.strip(),
                'chunk_index': chunk_index,
                'page_number': page_number,
                'start_char': start,
                'end_char': end
            })
            
            chunk_index += 1
            start = end - self.chunk_overlap  # Overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[Dict[str, any]]:
        """
        Process PDF and return chunks.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of chunk dictionaries
        """
        extraction_result = self.extract_text(pdf_path)
        all_chunks = []
        
        # Chunk text by page for better context
        for page_data in extraction_result['text_by_page']:
            page_chunks = self.chunk_text(
                page_data['text'],
                page_data['page_number']
            )
            all_chunks.extend(page_chunks)
        
        return {
            'chunks': all_chunks,
            'metadata': extraction_result['metadata']
        }

