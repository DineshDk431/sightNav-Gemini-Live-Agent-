"""
SightNav — Memory Manager (Semantic RAG)
========================================
Using FAISS and SentenceTransformers to load the rules from 
long_term_memory.json into a local vector database. 
This ensures we only feed Gemini the Top 5 most relevant 
rules, saving tokens and minimizing hallucinations.
"""

import os
import json
import faiss
import numpy as np
from src.utils.logger import Logger

# Note: We lazily import SentenceTransformer so we don't boot up PyTorch on boot
_embedder = None

MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'long_term_memory.json')

class MemoryManager:
    def __init__(self):
        self.rules = []
        self.index = None
        self.embedding_model_name = 'all-MiniLM-L6-v2'
        self._load_memory()

    def _get_embedder(self):
        global _embedder
        if _embedder is None:
            Logger.info(f"Loading sentence-transformer ({self.embedding_model_name})...")
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer(self.embedding_model_name)
        return _embedder

    def _load_memory(self):
        """Reads the JSON and rebuilds the FAISS index."""
        if not os.path.exists(MEMORY_FILE):
            self.rules = []
            return

        try:
            with open(MEMORY_FILE, 'r') as f:
                self.rules = json.load(f)
                
            if self.rules:
                Logger.info(f"Building semantic index for {len(self.rules)} memory rules...")
                model = self._get_embedder()
                embeddings = model.encode(self.rules, convert_to_numpy=True)
                
                # Create L2 FAISS Index
                dimension = embeddings.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
                self.index.add(embeddings)
        except Exception as e:
            Logger.error(f"FAISS Memory load failed: {e}")
            self.rules = []

    def query_top_k(self, intent: str, k: int = 5) -> list:
        """
        Retrieves the top K rules most semantically similar to the current intent.
        """
        if not self.rules or self.index is None:
            return []
            
        if len(self.rules) <= k:
            return self.rules # Just return all of them if memory is small

        try:
            model = self._get_embedder()
            query_vector = model.encode([intent], convert_to_numpy=True)
            
            # distances, indices
            D, I = self.index.search(query_vector, k)
            
            relevant_rules = []
            for idx in I[0]:
                if 0 <= idx < len(self.rules):
                    relevant_rules.append(self.rules[idx])
                    
            Logger.memory(f"Retrieved top {len(relevant_rules)} semantic rules for intent.")
            return relevant_rules
            
        except Exception as e:
            Logger.error(f"Semantic search failed: {e}")
            return self.rules[:k] # Fallback to returning the first K rules
