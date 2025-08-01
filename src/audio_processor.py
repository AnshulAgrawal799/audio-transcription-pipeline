"""
Audio Processing Module

Handles MP3 to WAV conversion with specific requirements:
- Converts MP3 to WAV format
- Sets sample rate to 16kHz
- Converts to mono channel
- Uses FFmpeg for conversion
- Maintains audio quality during conversion
"""

import logging
from pathlib import Path
from typing import Optional
import ffmpeg
from pydub import AudioSegment
from constants import SAMPLE_RATE, CHANNELS, MAX_FILE_SIZE_MB, SUPPORTED_AUDIO_EXTENSIONS

# Get logger for this module
logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles audio file processing and conversion."""
    
    def __init__(self, input_dir: str = "audio", output_dir: str = "output"):
        """
        Initialize the audio processor.
        
        Args:
            input_dir: Directory containing input audio files
            output_dir: Directory for processed audio files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.sample_rate = SAMPLE_RATE
        self.channels = CHANNELS
        
        # Output directory will be created by pipeline orchestrator
        
        logger.info(f"Audio processor initialized with input_dir={input_dir}, output_dir={output_dir}")
    
    def validate_audio_file(self, file_path: Path) -> bool:
        """
        Validate audio file existence and format.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        if not file_path.exists():
            logger.error(f"Audio file not found: {file_path}")
            return False
        
        if not file_path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
            logger.error(f"Unsupported audio format: {file_path.suffix}. Only {SUPPORTED_AUDIO_EXTENSIONS} are supported.")
            return False
        
        # Check file size (max 50MB as per FR-001)
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            logger.error(f"File size {file_size_mb:.2f}MB exceeds maximum limit of {MAX_FILE_SIZE_MB}MB")
            return False
        
        logger.info(f"Audio file validated: {file_path} ({file_size_mb:.2f}MB)")
        return True
    
    def convert_mp3_to_wav(self, input_file: str) -> Optional[str]:
        """
        Convert MP3 file to WAV format with specified parameters.
        
        Args:
            input_file: Name of the MP3 file in the input directory
            
        Returns:
            Optional[str]: Path to the converted WAV file, or None if conversion failed
        """
        input_path = self.input_dir / input_file
        
        if not self.validate_audio_file(input_path):
            return None
        
        # Generate unique output filename based on input file
        output_filename = f"{input_path.stem}_converted.wav"
        output_path = self.output_dir / output_filename
        
        try:
            logger.info(f"Starting conversion: {input_path} -> {output_path}")
            
            # Use FFmpeg for conversion with specific parameters
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec='pcm_s16le',  # 16-bit PCM
                ar=self.sample_rate,  # 16kHz sample rate
                ac=self.channels,     # mono channel
                loglevel='warning'
            )
            
            # Run the conversion
            ffmpeg.run(stream, overwrite_output=True)
            
            logger.info(f"Conversion completed successfully: {output_path}")
            return str(output_path)
            
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg conversion failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            return None
    
    def get_audio_info(self, file_path: str) -> Optional[dict]:
        """
        Get audio file information.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Optional[dict]: Audio file information
        """
        try:
            audio = AudioSegment.from_file(file_path)
            return {
                'duration_seconds': len(audio) / 1000,
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'frame_width': audio.sample_width,
                'file_size_mb': Path(file_path).stat().st_size / (1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Failed to get audio info: {e}")
            return None
    
    def process_audio_file(self, filename: str) -> Optional[str]:
        """
        Process an audio file through the complete pipeline.
        
        Args:
            filename: Name of the audio file to process
            
        Returns:
            Optional[str]: Path to the processed WAV file, or None if processing failed
        """
        logger.info(f"Processing audio file: {filename}")
        
        # Convert MP3 to WAV
        wav_path = self.convert_mp3_to_wav(filename)
        if not wav_path:
            logger.error(f"Failed to convert audio file: {filename}")
            return None
        
        # Get and log audio information
        audio_info = self.get_audio_info(wav_path)
        if audio_info:
            logger.info(f"Processed audio info: {audio_info}")
        
        return wav_path
    
    def list_audio_files(self) -> list:
        """
        List all MP3 files in the input directory.
        
        Returns:
            list: List of MP3 filenames
        """
        if not self.input_dir.exists():
            logger.warning(f"Input directory does not exist: {self.input_dir}")
            return []
        
        audio_files = [f.name for f in self.input_dir.glob("*.mp3")]
        logger.info(f"Found {len(audio_files)} MP3 files in {self.input_dir}")
        return audio_files


# Test function removed - use main.py for testing