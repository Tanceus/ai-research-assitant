"""Retrieval system for finding relevant document chunks."""
import numpy as np
from typing import List, Dict, Tuple
from app.embedding import EmbeddingGenerator
from app.config import settings
import faiss
import pickle
import os
from pathlib import Path


class VectorRetriever:
    """Retrieves relevant document chunks using vector similarity search."""
    
    def __init__(self, embedding_generator: EmbeddingGenerator):
        """
        Initialize the vector retriever.
        
        Args:
            embedding_generator: EmbeddingGenerator instance
        """
        self.embedding_generator = embedding_generator
        self.index = None
        self.chunks = []
        self.embedding_dim = embedding_generator.get_embedding_dimension()
        self.vector_store_path = settings.VECTOR_STORE_PATH
        self._ensure_vector_store_dir()
    
    def _ensure_vector_store_dir(self):
        """Ensure the vector store directory exists."""
        Path(self.vector_store_path).mkdir(parents=True, exist_ok=True)
    
    def add_chunks(self, chunks: List[Dict[str, any]]):
        """
        Add chunks to the vector store.
        
        Args:
            chunks: List of chunk dictionaries with 'content' key
        """
        if not chunks:
            return
        
        # Extract texts
        texts = [chunk['content'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_generator.generate_embeddings_batch(texts)
        
        # Initialize FAISS index if needed
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity (normalized)
        
        # Convert to float32 for FAISS
        embeddings = embeddings.astype('float32')
        
        # Add to index
        self.index.add(embeddings)
        
        # Store chunk metadata
        self.chunks.extend(chunks)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, any]]:
        """
        Search for relevant chunks.
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of relevant chunks with similarity scores
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        # Format results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk['similarity_score'] = float(distance)
                chunk['rank'] = i + 1
                results.append(chunk)
        
        return results
    
    def save(self, filepath: str = None):
        """Save the vector store to disk."""
        if filepath is None:
            filepath = os.path.join(self.vector_store_path, "vector_store.index")
        
        if self.index is not None:
            # Save FAISS index
            faiss.write_index(self.index, filepath)
            
            # Save chunks metadata
            chunks_file = filepath.replace(".index", "_chunks.pkl")
            with open(chunks_file, 'wb') as f:
                pickle.dump(self.chunks, f)
    
    def load(self, filepath: str = None):
        """Load the vector store from disk."""
        if filepath is None:
            filepath = os.path.join(self.vector_store_path, "vector_store.index")
        
        if os.path.exists(filepath):
            # Load FAISS index
            self.index = faiss.read_index(filepath)
            
            # Load chunks metadata
            chunks_file = filepath.replace(".index", "_chunks.pkl")
            if os.path.exists(chunks_file):
                with open(chunks_file, 'rb') as f:
                    self.chunks = pickle.load(f)
    
    def clear(self):
        """Clear all stored chunks and reset the index."""
        self.index = None
        self.chunks = []

