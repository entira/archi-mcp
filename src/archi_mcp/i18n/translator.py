"""Simple dictionary-based translator for ArchiMate multilingual support."""

from typing import Optional, Dict, Any
from .languages import AVAILABLE_LANGUAGES


class ArchiMateTranslator:
    """Simple translator using dictionary files for multiple language support."""
    
    def __init__(self, language: str = "en"):
        """Initialize translator with specified language.
        
        Args:
            language: Language code (e.g., "en", "sk")
        """
        self.language = language
        self.dictionary = AVAILABLE_LANGUAGES.get(language, AVAILABLE_LANGUAGES["en"])
    
    def translate_layer(self, layer: str) -> str:
        """Translate layer name.
        
        Args:
            layer: ArchiMate layer name (e.g., "Business", "Application")
            
        Returns:
            Translated layer name
        """
        return self.dictionary["layers"].get(layer, layer)
    
    def translate_relationship(self, relationship_type: str) -> str:
        """Translate relationship type.
        
        Args:
            relationship_type: ArchiMate relationship type (e.g., "Assignment", "Flow")
            
        Returns:
            Translated relationship name
        """
        return self.dictionary["relationships"].get(relationship_type, relationship_type.lower())
    
    def translate_element(self, element_type: str) -> str:
        """Translate element type.
        
        Args:
            element_type: ArchiMate element type (e.g., "Business_Function")
            
        Returns:
            Translated element name
        """
        return self.dictionary["elements"].get(element_type, element_type)
    
    def set_language(self, language: str) -> bool:
        """Change the current language.
        
        Args:
            language: Language code
            
        Returns:
            True if language was set successfully, False if language not found
        """
        if language in AVAILABLE_LANGUAGES:
            self.language = language
            self.dictionary = AVAILABLE_LANGUAGES[language]
            return True
        return False
    
    def get_available_languages(self) -> list:
        """Get list of available language codes.
        
        Returns:
            List of available language codes
        """
        return list(AVAILABLE_LANGUAGES.keys())
    
    def get_current_language(self) -> str:
        """Get current language code.
        
        Returns:
            Current language code
        """
        return self.language