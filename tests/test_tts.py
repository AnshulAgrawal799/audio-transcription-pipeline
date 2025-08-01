"""
Test TTS Module

Tests for the text-to-speech functionality using gTTS.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tts import TTSEngine


class TestTTSEngine:
    """Test cases for TTSEngine."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.tts_engine = TTSEngine(output_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_tts_engine_initialization(self):
        """Test TTS engine initialization."""
        assert self.tts_engine.output_dir == Path(self.temp_dir)
    
    def test_generate_speech_simple_text(self):
        """Test simple Tamil text to speech generation."""
        tamil_text = "வணக்கம் உலகம்"
        result = self.tts_engine.generate_speech(tamil_text, "test_speech")
        
        assert result is not None
        assert 'original_text' in result
        assert 'audio_file_path' in result
        assert 'audio_filename' in result
        assert result['original_text'] == tamil_text
        assert result['language_code'] == 'ta'
        assert result['audio_format'] == 'mp3'
        
        # Check if audio file was created
        audio_path = Path(result['audio_file_path'])
        assert audio_path.exists()
        assert audio_path.suffix == '.mp3'
        assert audio_path.stat().st_size > 1024  # More than 1KB
    
    def test_generate_speech_long_text(self):
        """Test longer Tamil text to speech generation."""
        tamil_text = "இது ஒரு நீண்ட உரை ஆகும். இது பல வாக்கியங்களைக் கொண்டுள்ளது."
        result = self.tts_engine.generate_speech(tamil_text, "test_long_speech")
        
        assert result is not None
        assert len(result['original_text']) > 0
        assert result['language_code'] == 'ta'
        
        # Check if audio file was created
        audio_path = Path(result['audio_file_path'])
        assert audio_path.exists()
        assert audio_path.stat().st_size > 1024
    
    def test_save_tts_metadata(self):
        """Test saving TTS metadata."""
        # Create mock TTS result
        tts_result = {
            'original_text': 'வணக்கம் உலகம்',
            'audio_file_path': str(Path(self.temp_dir) / 'test.mp3'),
            'audio_filename': 'test.mp3',
            'language_code': 'ta',
            'text_length': 12,
            'tts_timestamp': '2025-01-01T00:00:00',
            'audio_format': 'mp3'
        }
        
        # Save metadata
        success = self.tts_engine.save_tts_metadata(tts_result, "test")
        
        assert success is True
        
        # Check if metadata file was created
        metadata_file = Path(self.temp_dir) / "test_metadata.json"
        assert metadata_file.exists()
    
    def test_validate_tts_result(self):
        """Test TTS result validation."""
        # Create a temporary audio file for testing
        audio_file = Path(self.temp_dir) / "test_audio.mp3"
        with open(audio_file, 'wb') as f:
            f.write(b'fake audio data' * 100)  # Create a file with some content
        
        # Valid TTS result
        valid_result = {
            'original_text': 'வணக்கம் உலகம்',
            'audio_file_path': str(audio_file)
        }
        assert self.tts_engine.validate_tts_result(valid_result) is True
        
        # Invalid TTS result - empty original text
        invalid_result1 = {
            'original_text': '',
            'audio_file_path': str(audio_file)
        }
        assert self.tts_engine.validate_tts_result(invalid_result1) is False
        
        # Invalid TTS result - missing audio path
        invalid_result2 = {
            'original_text': 'வணக்கம் உலகம்',
            'audio_file_path': ''
        }
        assert self.tts_engine.validate_tts_result(invalid_result2) is False
        
        # Invalid TTS result - non-existent audio file
        invalid_result3 = {
            'original_text': 'வணக்கம் உலகம்',
            'audio_file_path': str(Path(self.temp_dir) / "nonexistent.mp3")
        }
        assert self.tts_engine.validate_tts_result(invalid_result3) is False
    
    def test_process_text_pipeline(self):
        """Test complete TTS pipeline."""
        tamil_text = "இது ஒரு சோதனை உரை ஆகும்."
        result = self.tts_engine.process_text(tamil_text, "pipeline_test")
        
        assert result is not None
        assert 'original_text' in result
        assert 'audio_file_path' in result
        assert result['language_code'] == 'ta'
        
        # Check if files were created
        audio_path = Path(result['audio_file_path'])
        metadata_file = Path(self.temp_dir) / "pipeline_test_metadata.json"
        
        assert audio_path.exists()
        assert metadata_file.exists()
        assert audio_path.stat().st_size > 1024
    
    def test_empty_text_handling(self):
        """Test handling of empty text input."""
        result = self.tts_engine.generate_speech("", "empty_test")
        assert result is None
    
    def test_whitespace_text_handling(self):
        """Test handling of whitespace-only text input."""
        result = self.tts_engine.generate_speech("   ", "whitespace_test")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__]) 