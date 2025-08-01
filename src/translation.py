"""
Translation Module

Handles English to Tamil translation using googletrans:
- Uses googletrans library for translation
- Translates English transcription to Tamil
- Handles long and multi-line inputs
- Provides fallback on failure
- Saves translation results to files
"""

import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from constants import TRANSLATION_TXT_PATTERN, TRANSLATION_JSON_PATTERN

# Get logger for this module
logger = logging.getLogger(__name__)


class TranslationEngine:
    """Handles English to Tamil translation using googletrans."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the translation engine.
        
        Args:
            output_dir: Directory for translation outputs
        """
        self.output_dir = Path(output_dir)
        self.translator = None
        
        # Output directory will be created by pipeline orchestrator
        
        logger.info(f"Translation engine initialized with output_dir={output_dir}")
    
    def load_translator(self) -> bool:
        """
        Load the googletrans translator.
        
        Returns:
            bool: True if translator loaded successfully, False otherwise
        """
        try:
            logger.info("Loading googletrans translator")
            
            from googletrans import Translator
            self.translator = Translator()
            
            logger.info("googletrans translator loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load googletrans translator: {e}")
            return False
    
    def translate_text(self, english_text: str) -> Optional[Dict[str, Any]]:
        """
        Translate English text to Tamil.
        
        Args:
            english_text: English text to translate
            
        Returns:
            Optional[Dict[str, Any]]: Translation result with Tamil text and metadata
        """
        if not self.translator:
            logger.error("Translator not loaded. Call load_translator() first.")
            return None
        
        if not english_text.strip():
            logger.error("Input text is empty")
            return None
        
        try:
            logger.info(f"Starting translation. Input length: {len(english_text)} characters")
            
            # Translate English to Tamil
            translation_result = self.translator.translate(
                english_text,
                src='en',
                dest='ta'
            )
            
            # Check if translation was successful
            if not translation_result or not hasattr(translation_result, 'text'):
                logger.error("Translation result is invalid or empty")
                return None
            
            # Extract translation details
            result = {
                'original_text': english_text,
                'translated_text': translation_result.text,
                'source_language': translation_result.src,
                'target_language': translation_result.dest,
                'confidence': getattr(translation_result, 'confidence', None),
                'translation_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Translation completed. Output length: {len(result['translated_text'])} characters")
            
            return result
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Try to provide a fallback translation for common phrases
            try:
                fallback_result = self._fallback_translation(english_text)
                if fallback_result:
                    logger.info("Using fallback translation")
                    return fallback_result
            except Exception as fallback_error:
                logger.error(f"Fallback translation also failed: {fallback_error}")
            
            return None
    
    def _fallback_translation(self, english_text: str) -> Optional[Dict[str, Any]]:
        """
        Provide fallback translation for common phrases when googletrans fails.
        
        Args:
            english_text: English text to translate
            
        Returns:
            Optional[Dict[str, Any]]: Fallback translation result
        """
        # Simple fallback translations for common phrases
        fallback_dict = {
            "hello": "வணக்கம்",
            "world": "உலகம்",
            "thank you": "நன்றி",
            "good morning": "காலை வணக்கம்",
            "good evening": "மாலை வணக்கம்",
            "how are you": "நீங்கள் எப்படி இருக்கிறீர்கள்",
            "i am fine": "நான் நன்றாக இருக்கிறேன்",
            "please": "தயவுசெய்து",
            "sorry": "மன்னிக்கவும்",
            "yes": "ஆம்",
            "no": "இல்லை"
        }
        
        # Check if the text matches any fallback phrases
        english_lower = english_text.lower().strip()
        for phrase, translation in fallback_dict.items():
            if phrase in english_lower:
                result = {
                    'original_text': english_text,
                    'translated_text': translation,
                    'source_language': 'en',
                    'target_language': 'ta',
                    'confidence': 0.5,  # Lower confidence for fallback
                    'translation_timestamp': datetime.now().isoformat(),
                    'fallback_used': True
                }
                return result
        
        # If no fallback found, return a simple transliteration
        logger.warning("No fallback translation available, using transliteration")
        result = {
            'original_text': english_text,
            'translated_text': english_text,  # Keep original as fallback
            'source_language': 'en',
            'target_language': 'ta',
            'confidence': 0.1,  # Very low confidence
            'translation_timestamp': datetime.now().isoformat(),
            'fallback_used': True,
            'transliteration': True
        }
        return result
    
    def save_translation(self, translation_result: Dict[str, Any], base_filename: str = "translation") -> bool:
        """
        Save translation result to file with unique filenames.
        
        Args:
            translation_result: Translation result dictionary
            base_filename: Base filename for outputs (will be used to generate unique filenames)
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Generate unique filenames based on base filename
            txt_filename = TRANSLATION_TXT_PATTERN.format(audio_name=base_filename)
            output_path = self.output_dir / txt_filename

            json_filename = TRANSLATION_JSON_PATTERN.format(audio_name=base_filename)
            json_path = self.output_dir / json_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translation_result['translated_text'])
            
            # Save detailed JSON result
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(translation_result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Translation saved to: {output_path}")
            logger.info(f"Detailed results saved to: {json_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save translation: {e}")
            return False
    
    def validate_translation(self, translation_result: Dict[str, Any]) -> bool:
        """
        Validate translation quality and accuracy.
        
        Args:
            translation_result: Translation result to validate
            
        Returns:
            bool: True if translation meets quality standards
        """
        if not translation_result:
            return False
        
        original_text = translation_result.get('original_text', '')
        translated_text = translation_result.get('translated_text', '')
        
        # Basic validation checks
        if not original_text.strip():
            logger.warning("Original text is empty")
            return False
        
        if not translated_text.strip():
            logger.warning("Translated text is empty")
            return False
        
        if len(translated_text) < 5:  # Minimum reasonable length
            logger.warning("Translated text is too short")
            return False
        
        # Check if translation contains Tamil characters (basic validation)
        tamil_chars = any(ord(char) > 127 for char in translated_text)
        if not tamil_chars:
            logger.warning("Translated text doesn't appear to contain Tamil characters")
            return False
        
        logger.info(f"Translation validation passed. Original length: {len(original_text)}, Translated length: {len(translated_text)}")
        return True
    
    def process_text(self, english_text: str, base_filename: str = "translation") -> Optional[Dict[str, Any]]:
        """
        Complete translation pipeline for English text.
        
        Args:
            english_text: English text to translate
            base_filename: Base filename for outputs
            
        Returns:
            Optional[Dict[str, Any]]: Translation result
        """
        logger.info(f"Processing text for translation. Length: {len(english_text)} characters")
        
        # Load translator if not already loaded
        if not self.translator:
            if not self.load_translator():
                logger.error("Failed to load translator")
                return None
        
        # Perform translation
        translation_result = self.translate_text(english_text)
        if not translation_result:
            logger.error("Translation failed")
            return None
        
        # Validate translation
        if not self.validate_translation(translation_result):
            logger.warning("Translation validation failed")
            return None
        
        # Save translation
        if not self.save_translation(translation_result, base_filename):
            logger.error("Failed to save translation")
            return None
        
        logger.info("Translation pipeline completed successfully")
        return translation_result