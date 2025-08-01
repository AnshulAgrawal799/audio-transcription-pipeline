"""
Test Translation Module

Tests for the translation functionality using googletrans.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from translation import TranslationEngine


class TestTranslationEngine:
    """Test cases for TranslationEngine."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.translation_engine = TranslationEngine(output_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_translation_engine_initialization(self):
        """Test translation engine initialization."""
        assert self.translation_engine.output_dir == Path(self.temp_dir)
        assert self.translation_engine.translator is None
    
    def test_load_translator(self):
        """Test translator loading."""
        success = self.translation_engine.load_translator()
        assert success is True
        assert self.translation_engine.translator is not None
    
    def test_translate_simple_text(self):
        """Test simple English to Tamil translation."""
        # Load translator
        self.translation_engine.load_translator()
        
        # Test translation
        english_text = "Hello, how are you?"
        result = self.translation_engine.translate_text(english_text)
        
        assert result is not None
        assert 'original_text' in result
        assert 'translated_text' in result
        assert result['original_text'] == english_text
        assert len(result['translated_text']) > 0
        assert result['source_language'] == 'en'
        assert result['target_language'] == 'ta'
    
    def test_translate_long_text(self):
        """Test translation of longer text."""
        # Load translator
        self.translation_engine.load_translator()
        
        # Test translation
        english_text = "This is a longer text to test translation capabilities. It should handle multiple sentences and paragraphs."
        result = self.translation_engine.translate_text(english_text)
        
        assert result is not None
        assert len(result['translated_text']) > 0
        assert result['source_language'] == 'en'
        assert result['target_language'] == 'ta'
    
    def test_save_translation(self):
        """Test saving translation results."""
        # Load translator
        self.translation_engine.load_translator()
        
        # Create mock translation result
        translation_result = {
            'original_text': 'Hello world',
            'translated_text': 'வணக்கம் உலகம்',
            'source_language': 'en',
            'target_language': 'ta',
            'translation_timestamp': '2025-01-01T00:00:00'
        }
        
        # Save translation
        success = self.translation_engine.save_translation(translation_result, "test")
        
        assert success is True
        
        # Check if files were created
        txt_file = Path(self.temp_dir) / "test_translation.txt"
        json_file = Path(self.temp_dir) / "test_translation_detailed.json"
        
        assert txt_file.exists()
        assert json_file.exists()
        
        # Check content
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert content == 'வணக்கம் உலகம்'
    
    def test_validate_translation(self):
        """Test translation validation."""
        # Valid translation
        valid_result = {
            'original_text': 'Hello world',
            'translated_text': 'வணக்கம் உலகம்'
        }
        assert self.translation_engine.validate_translation(valid_result) is True
        
        # Invalid translation - empty original
        invalid_result1 = {
            'original_text': '',
            'translated_text': 'வணக்கம் உலகம்'
        }
        assert self.translation_engine.validate_translation(invalid_result1) is False
        
        # Invalid translation - empty translated
        invalid_result2 = {
            'original_text': 'Hello world',
            'translated_text': ''
        }
        assert self.translation_engine.validate_translation(invalid_result2) is False
        
        # Invalid translation - too short
        invalid_result3 = {
            'original_text': 'Hello world',
            'translated_text': 'Hi'
        }
        assert self.translation_engine.validate_translation(invalid_result3) is False
    
    def test_process_text_pipeline(self):
        """Test complete translation pipeline."""
        # Load translator
        self.translation_engine.load_translator()
        
        # Test complete pipeline
        english_text = "This is a test of the translation pipeline."
        result = self.translation_engine.process_text(english_text, "pipeline_test")
        
        assert result is not None
        assert 'original_text' in result
        assert 'translated_text' in result
        assert len(result['translated_text']) > 0
        
        # Check if files were created
        txt_file = Path(self.temp_dir) / "pipeline_test_translation.txt"
        json_file = Path(self.temp_dir) / "pipeline_test_translation_detailed.json"
        
        assert txt_file.exists()
        assert json_file.exists()


if __name__ == "__main__":
    pytest.main([__file__]) 