"""
Hugging Face Service for NLP and text similarity
"""
from sentence_transformers import SentenceTransformer
from typing import Dict, Any, List
import numpy as np
from difflib import SequenceMatcher


class HuggingFaceService:
    """Service for Hugging Face NLP models"""
    
    def __init__(self):
        try:
            # Load sentence transformer model for semantic similarity
            self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load Hugging Face model: {e}")
            self.similarity_model = None
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        if not self.similarity_model:
            # Fallback to basic string similarity
            return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
        try:
            embeddings = self.similarity_model.encode([text1, text2])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            return float(similarity)
        except Exception as e:
            # Fallback to basic string similarity
            return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def fuzzy_match_names(self, name1: str, name2: str) -> Dict[str, Any]:
        """
        Perform fuzzy matching on provider names
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Dictionary with match results
        """
        # Basic string similarity
        basic_similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
        
        # Semantic similarity if model available
        semantic_similarity = self.calculate_semantic_similarity(name1, name2)
        
        # Combined score
        combined_score = (basic_similarity * 0.6 + semantic_similarity * 0.4)
        
        return {
            'basic_similarity': basic_similarity,
            'semantic_similarity': semantic_similarity,
            'combined_score': combined_score,
            'is_match': combined_score > 0.8
        }
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract named entities from text (simplified version)
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with extracted entities
        """
        # This is a simplified version
        # In production, you would use a proper NER model
        import re
        
        # Extract phone numbers
        phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        phones = phone_pattern.findall(text)
        
        # Extract emails
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = email_pattern.findall(text)
        
        # Extract addresses (basic pattern)
        address_pattern = re.compile(r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)')
        addresses = address_pattern.findall(text)
        
        return {
            'phones': phones,
            'emails': emails,
            'addresses': addresses
        }

