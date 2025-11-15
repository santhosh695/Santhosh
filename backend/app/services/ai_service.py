import json
import requests
from typing import List, Dict, Any
from flask import current_app
import time
import hashlib

class AIService:
    """
    AI Service for legal analysis using external APIs.
    Supports multiple providers for redundancy and cost optimization.
    """

    def __init__(self):
        self.providers = {
            'huggingface': HuggingFaceProvider(),
            'google_ai': GoogleAIProvider(),
            'mock': MockProvider()  # Fallback provider
        }
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 3600  # 1 hour cache TTL

    def analyze_fir_text(self, complaint_text: str) -> Dict[str, Any]:
        """
        Analyze FIR complaint text and suggest legal sections.

        Args:
            complaint_text (str): The FIR complaint text

        Returns:
            Dict containing analysis results
        """
        cache_key = self._generate_cache_key('fir_analysis', complaint_text)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        try:
            # Try providers in order of preference
            for provider_name, provider in self.providers.items():
                try:
                    result = provider.analyze_fir_text(complaint_text)
                    if result:
                        # Cache the result
                        self._set_cache(cache_key, result)
                        return result
                except Exception as e:
                    current_app.logger.warning(f"Provider {provider_name} failed: {str(e)}")
                    continue

            # If all providers fail, return basic analysis
            return self._get_basic_fir_analysis(complaint_text)

        except Exception as e:
            current_app.logger.error(f"FIR analysis failed: {str(e)}")
            return self._get_basic_fir_analysis(complaint_text)

    def format_complaint(self, original_text: str, category: str = None) -> Dict[str, Any]:
        """
        Format complaint text into legal structure.

        Args:
            original_text (str): Original complaint text
            category (str): Complaint category

        Returns:
            Dict containing formatted complaint and suggestions
        """
        cache_key = self._generate_cache_key('complaint_format', original_text, category)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        try:
            # Try providers in order of preference
            for provider_name, provider in self.providers.items():
                try:
                    result = provider.format_complaint(original_text, category)
                    if result:
                        # Cache the result
                        self._set_cache(cache_key, result)
                        return result
                except Exception as e:
                    current_app.logger.warning(f"Provider {provider_name} failed: {str(e)}")
                    continue

            # If all providers fail, return basic formatting
            return self._get_basic_complaint_format(original_text, category)

        except Exception as e:
            current_app.logger.error(f"Complaint formatting failed: {str(e)}")
            return self._get_basic_complaint_format(original_text, category)

    def search_legal_sections(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for relevant legal sections based on query.

        Args:
            query (str): Search query

        Returns:
            List of relevant legal sections
        """
        cache_key = self._generate_cache_key('legal_search', query)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        try:
            # Try providers in order of preference
            for provider_name, provider in self.providers.items():
                try:
                    result = provider.search_legal_sections(query)
                    if result:
                        # Cache the result
                        self._set_cache(cache_key, result)
                        return result
                except Exception as e:
                    current_app.logger.warning(f"Provider {provider_name} failed: {str(e)}")
                    continue

            # If all providers fail, return empty list
            return []

        except Exception as e:
            current_app.logger.error(f"Legal search failed: {str(e)}")
            return []

    def _generate_cache_key(self, *args) -> str:
        """Generate cache key from arguments."""
        key_string = '|'.join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_from_cache(self, key: str) -> Any:
        """Get value from cache if not expired."""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return value
            else:
                del self.cache[key]
        return None

    def _set_cache(self, key: str, value: Any) -> None:
        """Set value in cache with timestamp."""
        self.cache[key] = (value, time.time())

    def _get_basic_fir_analysis(self, complaint_text: str) -> Dict[str, Any]:
        """Basic FIR analysis when AI services are unavailable."""
        # Simple keyword-based analysis
        keywords = self._extract_keywords(complaint_text)
        basic_sections = []

        # Map keywords to potential sections
        section_mappings = {
            'theft': ['IPC 379', 'IPC 380'],
            'fraud': ['IPC 420'],
            'assault': ['IPC 323', 'IPC 324'],
            'murder': ['IPC 302', 'IPC 304'],
            'harassment': ['IPC 354', 'IPC 506'],
            'property': ['IPC 447', 'IPC 448'],
            'vehicle': ['IPC 279', 'IPC 336'],
            'domestic': ['IPC 498A'],
            'cyber': ['IT Act 66', 'IT Act 67']
        }

        for keyword in keywords:
            if keyword in section_mappings:
                for section_ref in section_mappings[keyword]:
                    basic_sections.append({
                        'section': section_ref,
                        'confidence': 0.5,
                        'reason': f"Keyword match: '{keyword}'"
                    })

        return {
            'analysis': f"Basic analysis of complaint containing {len(complaint_text)} characters. Keywords found: {', '.join(keywords)}",
            'suggested_sections': basic_sections[:5],  # Limit to 5 suggestions
            'structured_fir': {
                'title': 'First Information Report',
                'sections': [
                    {
                        'heading': 'Complaint Details',
                        'content': complaint_text
                    },
                    {
                        'heading': 'Possible Legal Sections',
                        'content': ', '.join([s['section'] for s in basic_sections[:3]])
                    }
                ]
            },
            'confidence_score': 0.3,
            'requires_review': True
        }

    def _get_basic_complaint_format(self, original_text: str, category: str = None) -> Dict[str, Any]:
        """Basic complaint formatting when AI services are unavailable."""
        from datetime import datetime

        formatted_text = f"""
FORMAL COMPLAINT

Date: {datetime.now().strftime('%d/%m/%Y')}
Category: {category or 'General Complaint'}

Details of Complaint:
{original_text}

Action Required:
This matter requires immediate attention and appropriate action as per applicable laws and regulations.

Expected Resolution:
[To be filled based on specific circumstances]

Contact Information:
Name: [Your Name]
Email: [Your Email]
Phone: [Your Phone Number]

Declaration:
I hereby declare that the information provided above is true to the best of my knowledge.

Signature: ___________________
Date: ___________________
        """.strip()

        suggestions = {
            'improvements': [
                'Add specific dates and times of incidents',
                'Include names of individuals involved',
                'Add location details',
                'Attach supporting evidence if available',
                'Specify desired resolution'
            ],
            'recommended_actions': [
                'Submit to appropriate authority',
                'Keep a copy for your records',
                'Follow up if no response within reasonable time',
                'Consider seeking legal advice if needed'
            ]
        }

        return {
            'formatted_complaint': formatted_text,
            'suggestions': suggestions,
            'confidence_score': 0.4,
            'requires_review': True
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using simple frequency analysis."""
        import re

        # Common legal keywords
        legal_keywords = [
            'theft', 'fraud', 'assault', 'murder', 'harassment', 'property',
            'vehicle', 'domestic', 'cyber', 'threat', 'blackmail', 'extortion',
            'cheating', 'criminal', 'illegal', 'unauthorized', 'forgery'
        ]

        # Find keywords in text
        text_lower = text.lower()
        found_keywords = []

        for keyword in legal_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)

        return found_keywords[:10]  # Limit to 10 keywords


class HuggingFaceProvider:
    """HuggingFace Inference API provider."""

    def __init__(self):
        self.api_key = current_app.config.get('HUGGINGFACE_API_KEY')
        self.base_url = "https://api-inference.huggingface.co/models"

    def analyze_fir_text(self, complaint_text: str) -> Dict[str, Any]:
        """Analyze FIR text using HuggingFace models."""
        if not self.api_key:
            raise Exception("HuggingFace API key not configured")

        # For now, return None as this requires specific model setup
        return None

    def format_complaint(self, original_text: str, category: str = None) -> Dict[str, Any]:
        """Format complaint using HuggingFace models."""
        if not self.api_key:
            raise Exception("HuggingFace API key not configured")

        return None

    def search_legal_sections(self, query: str) -> List[Dict[str, Any]]:
        """Search legal sections using HuggingFace models."""
        if not self.api_key:
            raise Exception("HuggingFace API key not configured")

        return None


class GoogleAIProvider:
    """Google AI API provider."""

    def __init__(self):
        self.api_key = current_app.config.get('GOOGLE_AI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def analyze_fir_text(self, complaint_text: str) -> Dict[str, Any]:
        """Analyze FIR text using Google AI models."""
        if not self.api_key:
            raise Exception("Google AI API key not configured")

        return None

    def format_complaint(self, original_text: str, category: str = None) -> Dict[str, Any]:
        """Format complaint using Google AI models."""
        if not self.api_key:
            raise Exception("Google AI API key not configured")

        return None

    def search_legal_sections(self, query: str) -> List[Dict[str, Any]]:
        """Search legal sections using Google AI models."""
        if not self.api_key:
            raise Exception("Google AI API key not configured")

        return None


class MockProvider:
    """Mock provider for testing and fallback."""

    def analyze_fir_text(self, complaint_text: str) -> Dict[str, Any]:
        """Mock FIR analysis."""
        return {
            'analysis': f"Mock analysis of complaint text: {complaint_text[:100]}...",
            'suggested_sections': [
                {'section': 'IPC 379', 'confidence': 0.8, 'reason': 'Mock suggestion'},
                {'section': 'IPC 420', 'confidence': 0.6, 'reason': 'Mock suggestion'}
            ],
            'structured_fir': {
                'title': 'Mock FIR Analysis',
                'sections': [
                    {'heading': 'Mock Section', 'content': 'Mock content'}
                ]
            },
            'confidence_score': 0.5,
            'requires_review': True
        }

    def format_complaint(self, original_text: str, category: str = None) -> Dict[str, Any]:
        """Mock complaint formatting."""
        return {
            'formatted_complaint': f"Mock formatted complaint: {original_text[:100]}...",
            'suggestions': {
                'improvements': ['Mock improvement 1', 'Mock improvement 2'],
                'recommended_actions': ['Mock action 1', 'Mock action 2']
            },
            'confidence_score': 0.4,
            'requires_review': True
        }

    def search_legal_sections(self, query: str) -> List[Dict[str, Any]]:
        """Mock legal section search."""
        return [
            {
                'section': 'IPC 302',
                'title': 'Mock Section Title',
                'description': 'Mock description',
                'confidence': 0.7
            }
        ]


# Global AI service instance
ai_service = AIService()