import json
import os
from typing import Dict, Any, List
from flask import current_app

class TranslationService:
    """
    Translation service for multilingual support.
    Supports English, Hindi, Tamil, and Telugu languages.
    """

    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'हिन्दी (Hindi)',
            'ta': 'தமிழ் (Tamil)',
            'te': 'తెలుగు (Telugu)'
        }
        self.default_language = 'en'
        self.translation_cache = {}
        self.ui_translations = self._load_ui_translations()

    def translate_text(self, text: str, target_language: str = 'en', source_language: str = 'auto') -> Dict[str, Any]:
        """
        Translate text to target language.

        Args:
            text (str): Text to translate
            target_language (str): Target language code
            source_language (str): Source language code

        Returns:
            Dict containing translation result
        """
        if not text or not text.strip():
            return {
                'original_text': text,
                'translated_text': text,
                'source_language': source_language,
                'target_language': target_language,
                'confidence': 1.0
            }

        if target_language == self.default_language:
            return {
                'original_text': text,
                'translated_text': text,
                'source_language': source_language,
                'target_language': target_language,
                'confidence': 1.0
            }

        # Check cache first
        cache_key = f"{source_language}:{target_language}:{hash(text)}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]

        try:
            # Try Google Translate API if available
            if current_app.config.get('GOOGLE_TRANSLATE_API_KEY'):
                result = self._translate_with_google(text, target_language, source_language)
            else:
                # Use basic translation mappings
                result = self._translate_with_mappings(text, target_language, source_language)

            # Cache the result
            self.translation_cache[cache_key] = result
            return result

        except Exception as e:
            current_app.logger.error(f"Translation failed: {str(e)}")
            # Return original text if translation fails
            return {
                'original_text': text,
                'translated_text': text,
                'source_language': source_language,
                'target_language': target_language,
                'confidence': 0.0,
                'error': 'Translation service unavailable'
            }

    def translate_ui_string(self, key: str, language: str = 'en') -> str:
        """
        Translate UI string by key.

        Args:
            key (str): Translation key
            language (str): Target language code

        Returns:
            str: Translated string
        """
        if language == self.default_language:
            return key

        try:
            translations = self.ui_translations.get(language, {})
            return translations.get(key, key)
        except Exception:
            return key

    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages."""
        return self.supported_languages

    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported."""
        return language_code in self.supported_languages

    def translate_legal_document(self, document_data: Dict[str, Any], target_language: str = 'en') -> Dict[str, Any]:
        """
        Translate legal document content.

        Args:
            document_data (Dict): Document data to translate
            target_language (str): Target language code

        Returns:
            Dict with translated content
        """
        if target_language == self.default_language:
            return document_data

        translated_data = document_data.copy()

        # Translate common fields
        text_fields = [
            'complaint_text', 'original_text', 'formatted_complaint',
            'ai_analysis', 'description', 'section_title'
        ]

        for field in text_fields:
            if field in document_data and document_data[field]:
                result = self.translate_text(document_data[field], target_language)
                translated_data[field] = result['translated_text']

        # Translate structured content
        if 'structured_fir' in document_data:
            translated_data['structured_fir'] = self._translate_structured_content(
                document_data['structured_fir'], target_language
            )

        return translated_data

    def _load_ui_translations(self) -> Dict[str, Dict[str, str]]:
        """Load UI translation strings."""
        translations = {
            'en': {},  # English is the base language
            'hi': {
                'Login': 'लॉगिन',
                'Register': 'रजिस्टर',
                'Logout': 'लॉगआउट',
                'Dashboard': 'डैशबोर्ड',
                'Profile': 'प्रोफाइल',
                'FIR': 'एफआईआर',
                'Complaint': 'शिकायत',
                'Legal Search': 'कानूनी खोज',
                'Submit': 'जमा करें',
                'Cancel': 'रद्द करें',
                'Save': 'सहेजें',
                'Delete': 'हटाएं',
                'Edit': 'संपादित करें',
                'Search': 'खोजें',
                'Download': 'डाउनलोड',
                'Upload': 'अपलोड',
                'Name': 'नाम',
                'Email': 'ईमेल',
                'Phone': 'फोन',
                'Password': 'पासवर्ड',
                'Confirm Password': 'पासवर्ड की पुष्टि करें',
                'First Information Report': 'प्रथम सूचना रिपोर्ट',
                'Police Portal': 'पुलिस पोर्टल',
                'Public Portal': 'सार्वजनिक पोर्टल',
                'Incident Details': 'घटना का विवरण',
                'Complainant Information': 'शिकायतकर्ता की जानकारी',
                'Legal Sections': 'कानूनी धाराएं',
                'Evidence': 'सबूत'
            },
            'ta': {
                'Login': 'உள்ளே பதிவு',
                'Register': 'பதிவு',
                'Logout': 'வெளியேறு',
                'Dashboard': 'டாஷ்போர்டு',
                'Profile': 'சுயவிவரம்',
                'FIR': 'எஃப்ஐஆர்',
                'Complaint': 'புகார்',
                'Legal Search': 'சட்ட தேடல்',
                'Submit': 'சமர்ப்பிக்கவும்',
                'Cancel': 'ரத்துசெய்',
                'Save': 'சேமிக்கவும்',
                'Delete': 'நீக்கு',
                'Edit': 'தொகு',
                'Search': 'தேடு',
                'Download': 'பதிவிறக்கவும்',
                'Upload': 'பதிவேற்றவும்',
                'Name': 'பெயர்',
                'Email': 'மின்னஞ்சல்',
                'Phone': 'தொலைபேசி',
                'Password': 'கடவுச்சொல்',
                'Confirm Password': 'கடவுச்சொல்லை உறுதிப்படுத்தவும்',
                'First Information Report': 'முதல் தகவல் அறிக்கை',
                'Police Portal': 'போலீஸ் போர்டல்',
                'Public Portal': 'பொது போர்டல்',
                'Incident Details': 'சம்பவ விவரங்கள்',
                'Complainant Information': 'புகாரளர் தகவல்',
                'Legal Sections': 'சட்ட பிரிவுகள்',
                'Evidence': 'ஆதாரம்'
            },
            'te': {
                'Login': 'లాగిన్',
                'Register': 'నమోదు చేయండి',
                'Logout': 'లాగ్అవుట్',
                'Dashboard': 'డాష్బోర్డ్',
                'Profile': 'ప్రొఫైల్',
                'FIR': 'ఎఫ్ఐఆర్',
                'Complaint': 'ఫిర్యాదు',
                'Legal Search': 'చట్టపరమైన శోధన',
                'Submit': 'సమర్పించండి',
                'Cancel': 'రద్దుచేయండి',
                'Save': 'సేవ్ చేయండి',
                'Delete': 'తొలగించండి',
                'Edit': 'సవరించండి',
                'Search': 'వెతకండి',
                'Download': 'డౌన్‌లోడ్ చేయండి',
                'Upload': 'అప్‌లోడ్ చేయండి',
                'Name': 'పేరు',
                'Email': 'ఇమెయిల్',
                'Phone': 'ఫోన్',
                'Password': 'పాస్‌వర్డ్',
                'Confirm Password': 'పాస్‌వర్డ్‌ని నిర్ధారించండి',
                'First Information Report': 'మొదటి సమాచార నివేదిక',
                'Police Portal': 'పోలీస్ పోర్టల్',
                'Public Portal': 'పబ్లిక్ పోర్టల్',
                'Incident Details': 'సంఘటన వివరాలు',
                'Complainant Information': 'ఫిర్యాదీదారుడి సమాచారం',
                'Legal Sections': 'చట్టపరమైన సెక్షన్లు',
                'Evidence': 'ఆధారాలు'
            }
        }

        return translations

    def _translate_with_google(self, text: str, target_language: str, source_language: str) -> Dict[str, Any]:
        """Translate using Google Translate API."""
        try:
            import requests

            api_key = current_app.config.get('GOOGLE_TRANSLATE_API_KEY')
            url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"

            data = {
                'q': text,
                'target': target_language,
                'source': source_language if source_language != 'auto' else None,
                'format': 'text'
            }

            response = requests.post(url, data=data)
            response.raise_for_status()

            result = response.json()
            translated_text = result['data']['translations'][0]['translatedText']
            detected_language = result['data']['translations'][0].get('detectedSourceLanguage', source_language)

            return {
                'original_text': text,
                'translated_text': translated_text,
                'source_language': detected_language,
                'target_language': target_language,
                'confidence': 0.9,
                'provider': 'google'
            }

        except Exception as e:
            current_app.logger.error(f"Google Translate API error: {str(e)}")
            raise e

    def _translate_with_mappings(self, text: str, target_language: str, source_language: str) -> Dict[str, Any]:
        """
        Basic translation using predefined mappings.
        This is a fallback method with limited functionality.
        """
        # Basic legal term translations
        legal_translations = {
            'hi': {
                'theft': 'चोरी',
                'murder': 'हत्या',
                'assault': 'मारपीट',
                'fraud': 'धोखाधड़ी',
                'harassment': 'उत्पीड़न',
                'complaint': 'शिकायत',
                'police': 'पुलिस',
                'court': 'अदालत',
                'legal': 'कानूनी',
                'evidence': 'सबूत',
                'witness': 'गवाह',
                'victim': 'पीड़ित',
                'accused': 'अभियुक्त',
                'section': 'धारा',
                'punishment': 'सजा',
                'bailable': 'जमानतीय',
                'cognizable': 'अपराध स्वीकार्य'
            },
            'ta': {
                'theft': 'திருட்டு',
                'murder': 'கொலை',
                'assault': 'தாக்குதல்',
                'fraud': 'மோசடி',
                'harassment': 'துன்புறுத்தல்',
                'complaint': 'புகார்',
                'police': 'போலீஸ்',
                'court': 'நீதிமன்றம்',
                'legal': 'சட்ட',
                'evidence': 'ஆதாரம்',
                'witness': 'சாட்சி',
                'victim': 'பாதிக்கப்பட்டவர்',
                'accused': 'குற்றவாளி',
                'section': 'பிரிவு',
                'punishment': 'தண்டனை',
                'bailable': 'ஜாமீன் செலுத்தக்கூடிய',
                'cognizable': 'குற்றம் அங்கீகரிக்கப்பட்ட'
            },
            'te': {
                'theft': 'దొంగతనం',
                'murder': 'హత్య',
                'assault': 'దాడి',
                'fraud': 'మోసం',
                'harassment': 'వేధింపులు',
                'complaint': 'ఫిర్యాదు',
                'police': 'పోలీస్',
                'court': 'కోర్టు',
                'legal': 'చట్టపరమైన',
                'evidence': 'ఆధారాలు',
                'witness': 'సాక్షి',
                'victim': 'బాధితుడు',
                'accused': 'నిందితుడు',
                'section': 'సెక్షన్',
                'punishment': 'శిక్ష',
                'bailable': 'బెయిల్',
                'cognizable': 'క్రిమినల్'
            }
        }

        translations = legal_translations.get(target_language, {})
        translated_text = text.lower()

        # Replace known terms
        for english_term, translation in translations.items():
            translated_text = translated_text.replace(english_term, translation)

        return {
            'original_text': text,
            'translated_text': translated_text,
            'source_language': source_language,
            'target_language': target_language,
            'confidence': 0.3,  # Low confidence for basic mapping
            'provider': 'mapping'
        }

    def _translate_structured_content(self, content: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """Translate structured content like FIR sections."""
        if not isinstance(content, dict):
            return content

        translated_content = {}

        for key, value in content.items():
            if isinstance(value, str):
                result = self.translate_text(value, target_language)
                translated_content[key] = result['translated_text']
            elif isinstance(value, list):
                translated_list = []
                for item in value:
                    if isinstance(item, str):
                        result = self.translate_text(item, target_language)
                        translated_list.append(result['translated_text'])
                    elif isinstance(item, dict):
                        translated_list.append(self._translate_structured_content(item, target_language))
                    else:
                        translated_list.append(item)
                translated_content[key] = translated_list
            elif isinstance(value, dict):
                translated_content[key] = self._translate_structured_content(value, target_language)
            else:
                translated_content[key] = value

        return translated_content

    def clear_cache(self):
        """Clear translation cache."""
        self.translation_cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get translation cache statistics."""
        return {
            'cache_size': len(self.translation_cache),
            'supported_languages': self.supported_languages,
            'default_language': self.default_language
        }


# Global translation service instance
translation_service = TranslationService()