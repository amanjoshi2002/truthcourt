import json
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import pickle
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGStore:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.encoder = SentenceTransformer(model_name)
        self.cases = []
        self.embeddings = None
        self.cache_file = 'case_cache.pkl'
        self.load_cache()
        logger.info(f"RAGStore initialized with model: {model_name}")
    
    def load_cache(self):
        """Load cached cases if available"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                self.cases = cached_data['cases']
                self.embeddings = cached_data['embeddings']
                logger.info(f"Loaded {len(self.cases)} cases from cache")
        else:
            logger.info("No cache file found, starting with empty store")
    
    def save_cache(self):
        """Save cases to cache"""
        with open(self.cache_file, 'wb') as f:
            pickle.dump({
                'cases': self.cases,
                'embeddings': self.embeddings
            }, f)
        logger.info(f"Saved {len(self.cases)} cases to cache")
    
    def add_case(self, case: Dict):
        """Add a new case to the store"""
        # Create case embedding
        case_text = f"{case['topic']} {case['verdict']} {case['key_evidence']}"
        case_embedding = self.encoder.encode([case_text])[0]
        
        # Initialize embeddings array if first case
        if self.embeddings is None:
            self.embeddings = case_embedding.reshape(1, -1)
        else:
            self.embeddings = np.vstack([self.embeddings, case_embedding.reshape(1, -1)])
        
        self.cases.append(case)
        self.save_cache()
        logger.info(f"Added new case: {case['topic'][:100]}...")
    
    def find_similar_cases(self, query: str, threshold: float = 0.8) -> List[Dict]:
        """Find similar cases based on semantic similarity"""
        if not self.cases:
            logger.info("No cases in store to compare against")
            return []
            
        # Encode query
        query_embedding = self.encoder.encode([query]).reshape(1, -1)
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get cases above threshold
        similar_cases = []
        for idx, similarity in enumerate(similarities):
            if similarity >= threshold:
                case = self.cases[idx].copy()
                case['similarity'] = float(similarity)
                similar_cases.append(case)
        
        similar_cases = sorted(similar_cases, key=lambda x: x['similarity'], reverse=True)
        logger.info(f"Found {len(similar_cases)} similar cases for query: {query[:100]}...")
        return similar_cases