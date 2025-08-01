"""
Unit tests for AudioProcessor module
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import shutil

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_processor import AudioProcessor


class TestAudioProcessor(unittest.TestCase):
    """Test cases for AudioProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        self.input_dir.mkdir()
        self.output_dir.mkdir()
        
        # Create a mock MP3 file
        self.mock_mp3 = self.input_dir / "test.mp3"
        self.mock_mp3.write_bytes(b"mock mp3 content")
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test AudioProcessor initialization."""
        processor = AudioProcessor(str(self.input_dir), str(self.output_dir))
        
        self.assertEqual(processor.input_dir, self.input_dir)
        self.assertEqual(processor.output_dir, self.output_dir)
        self.assertEqual(processor.sample_rate, 16000)
        self.assertEqual(processor.channels, 1)
    
    def test_validate_audio_file_valid(self):
        """Test audio file validation with valid file."""
        processor = AudioProcessor(str(self.input_dir), str(self.output_dir))
        
        result = processor.validate_audio_file(self.mock_mp3)
        self.assertTrue(result)
    
    def test_validate_audio_file_nonexistent(self):
        """Test audio file validation with nonexistent file."""
        processor = AudioProcessor(str(self.input_dir), str(self.output_dir))
        
        nonexistent_file = self.input_dir / "nonexistent.mp3"
        result = processor.validate_audio_file(nonexistent_file)
        self.assertFalse(result)
    
    def test_validate_audio_file_wrong_format(self):
        """Test audio file validation with wrong format."""
        processor = AudioProcessor(str(self.input_dir), str(self.output_dir))
        
        wrong_format_file = self.input_dir / "test.wav"
        wrong_format_file.write_bytes(b"mock content")
        
        result = processor.validate_audio_file(wrong_format_file)
        self.assertFalse(result)
    
    def test_list_audio_files(self):
        """Test listing audio files."""
        processor = AudioProcessor(str(self.input_dir), str(self.output_dir))
        
        # Create additional MP3 files
        (self.input_dir / "audio1.mp3").write_bytes(b"content1")
        (self.input_dir / "audio2.mp3").write_bytes(b"content2")
        
        files = processor.list_audio_files()
        self.assertEqual(len(files), 3)  # test.mp3, audio1.mp3, audio2.mp3
        self.assertIn("test.mp3", files)
        self.assertIn("audio1.mp3", files)
        self.assertIn("audio2.mp3", files)
    
    @patch('audio_processor.ffmpeg')
    def test_convert_mp3_to_wav_success(self, mock_ffmpeg):
        """Test successful MP3 to WAV conversion."""
        processor = AudioProcessor(str(self.input_dir), str(self.output_dir))
        
        # Mock successful conversion
        mock_ffmpeg.input.return_value = MagicMock()
        mock_ffmpeg.output.return_value = MagicMock()
        mock_ffmpeg.run.return_value = None
        
        result = processor.convert_mp3_to_wav("test.mp3")
        
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith("test_converted.wav"))
    
    @patch('audio_processor.ffmpeg')
    def test_convert_mp3_to_wav_failure(self, mock_ffmpeg):
        """Test failed MP3 to WAV conversion."""
        processor = AudioProcessor(str(self.input_dir), str(self.output_dir))
        
        # Mock failed conversion
        mock_ffmpeg.input.side_effect = Exception("FFmpeg error")
        
        result = processor.convert_mp3_to_wav("test.mp3")
        
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main() 