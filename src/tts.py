"""
Text-to-Speech Module

Handles Tamil text-to-speech using gTTS:
- Uses gTTS for Tamil voice generation
- Converts UTF-8 Tamil text into natural speech
- Saves output as MP3 or WAV
- Supports language code 'ta'
- Provides audio file path for playback
"""

import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from constants import TTS_AUDIO_PATTERN, TTS_METADATA_PATTERN

# Get logger for this module
logger = logging.getLogger(__name__)


class TTSEngine:
    """Handles Tamil text-to-speech using gTTS."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the TTS engine.
        
        Args:
            output_dir: Directory for TTS outputs
        """
        self.output_dir = Path(output_dir)
        
        # Output directory will be created by pipeline orchestrator
        
        logger.info(f"TTS engine initialized with output_dir={output_dir}")
    
    def generate_speech(self, tamil_text: str, base_filename: str = "tamil_speech") -> Optional[Dict[str, Any]]:
        """
        Generate Tamil speech from text using gTTS.
        
        Args:
            tamil_text: Tamil text to convert to speech
            base_filename: Base filename for output audio file
            
        Returns:
            Optional[Dict[str, Any]]: TTS result with audio file path and metadata
        """
        if not tamil_text.strip():
            logger.error("Input text is empty")
            return None
        
        try:
            logger.info(f"Starting TTS generation. Text length: {len(tamil_text)} characters")
            
            from gtts import gTTS
            
            # Generate speech using gTTS
            tts = gTTS(text=tamil_text, lang='ta', slow=False)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = TTS_AUDIO_PATTERN.format(base_filename=base_filename, timestamp=timestamp)
            audio_path = self.output_dir / audio_filename
            
            # Save audio file
            tts.save(str(audio_path))
            
            # Create result dictionary
            result = {
                'original_text': tamil_text,
                'audio_file_path': str(audio_path),
                'audio_filename': audio_filename,
                'language_code': 'ta',
                'text_length': len(tamil_text),
                'tts_timestamp': datetime.now().isoformat(),
                'audio_format': 'mp3'
            }
            
            logger.info(f"TTS generation completed. Audio saved to: {audio_path}")
            return result
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None
    
    def save_tts_metadata(self, tts_result: Dict[str, Any], base_filename: str = "tamil_speech") -> bool:
        """
        Save TTS metadata to JSON file.
        
        Args:
            tts_result: TTS result dictionary
            base_filename: Base filename for metadata file
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Generate metadata filename
            metadata_filename = TTS_METADATA_PATTERN.format(base_filename=base_filename)
            metadata_path = self.output_dir / metadata_filename
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(tts_result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"TTS metadata saved to: {metadata_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save TTS metadata: {e}")
            return False
    
    def validate_tts_result(self, tts_result: Dict[str, Any]) -> bool:
        """
        Validate TTS generation result.
        
        Args:
            tts_result: TTS result to validate
            
        Returns:
            bool: True if TTS result meets quality standards
        """
        if not tts_result:
            return False
        
        audio_path = tts_result.get('audio_file_path', '')
        original_text = tts_result.get('original_text', '')
        
        # Basic validation checks
        if not original_text.strip():
            logger.warning("Original text is empty")
            return False
        
        if not audio_path:
            logger.warning("Audio file path is missing")
            return False
        
        # Check if audio file exists and has reasonable size
        audio_file = Path(audio_path)
        if not audio_file.exists():
            logger.warning("Audio file does not exist")
            return False
        
        file_size = audio_file.stat().st_size
        if file_size < 1024:  # Less than 1KB
            logger.warning(f"Audio file is too small: {file_size} bytes")
            return False
        
        logger.info(f"TTS validation passed. Audio file size: {file_size} bytes")
        return True
    
    def process_text(self, tamil_text: str, base_filename: str = "tamil_speech") -> Optional[Dict[str, Any]]:
        """
        Complete TTS pipeline for Tamil text.
        
        Args:
            tamil_text: Tamil text to convert to speech
            base_filename: Base filename for outputs
            
        Returns:
            Optional[Dict[str, Any]]: TTS result
        """
        logger.info(f"Processing text for TTS. Length: {len(tamil_text)} characters")
        
        # Generate speech
        tts_result = self.generate_speech(tamil_text, base_filename)
        if not tts_result:
            logger.error("TTS generation failed")
            return None
        
        # Validate TTS result
        if not self.validate_tts_result(tts_result):
            logger.warning("TTS validation failed")
            return None
        
        # Save metadata
        if not self.save_tts_metadata(tts_result, base_filename):
            logger.error("Failed to save TTS metadata")
            return None
        
        logger.info("TTS pipeline completed successfully")
        return tts_result