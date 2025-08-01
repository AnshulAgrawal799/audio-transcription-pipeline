"""
Audio Transcription & Translation Pipeline

A complete local Python pipeline that processes Tamil audio files,
transcribes them to English text using OpenAI's Whisper, and sends
the results to Google's Gemini API for further processing.
"""

__version__ = "1.0.0"
__author__ = "Audio Transcription Pipeline Team"

from .audio_processor import AudioProcessor
from .transcription import TranscriptionEngine
from .api_client import GeminiAPIClient
from .pipeline import AudioTranscriptionPipeline

__all__ = [
    'AudioProcessor',
    'TranscriptionEngine', 
    'GeminiAPIClient',
    'AudioTranscriptionPipeline'
] 