"""
Pipeline Orchestrator Module

Coordinates all pipeline components with sequential processing:
- Coordinates all pipeline steps sequentially
- Provides progress feedback
- Implements proper error handling
- Logs all operations for debugging
"""

import os
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from audio_processor import AudioProcessor
from transcription import TranscriptionEngine
from api_client import GeminiAPIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AudioTranscriptionPipeline:
    """Main pipeline orchestrator for audio transcription and API processing."""
    
    def __init__(self, input_dir: str = "audio", output_dir: str = "output"):
        """
        Initialize the pipeline.
        
        Args:
            input_dir: Directory containing input audio files
            output_dir: Directory for all outputs
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # Initialize components
        self.audio_processor = AudioProcessor(input_dir, output_dir)
        self.transcription_engine = TranscriptionEngine(output_dir=output_dir)
        self.api_client = GeminiAPIClient(output_dir=output_dir)
        
        # Pipeline state
        self.current_file = None
        self.pipeline_start_time = None
        self.step_results = {}
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info("Audio Transcription Pipeline initialized")
    
    def validate_environment(self) -> bool:
        """
        Validate the pipeline environment and dependencies.
        
        Returns:
            bool: True if environment is valid, False otherwise
        """
        logger.info("Validating pipeline environment...")
        
        # Check input directory
        if not self.input_dir.exists():
            logger.error(f"Input directory does not exist: {self.input_dir}")
            return False
        
        # Check for audio files
        audio_files = self.audio_processor.list_audio_files()
        if not audio_files:
            logger.error(f"No MP3 files found in {self.input_dir}")
            return False
        
        # Check API key
        if not self.api_client.validate_api_key():
            logger.error("API key validation failed")
            return False
        
        logger.info(f"Environment validation passed. Found {len(audio_files)} audio files")
        return True
    
    def process_audio_step(self, audio_file: str) -> Optional[str]:
        """
        Process audio file through the audio processing step.
        
        Args:
            audio_file: Name of the audio file to process
            
        Returns:
            Optional[str]: Path to processed WAV file
        """
        logger.info(f"Step 1: Audio Processing - {audio_file}")
        
        try:
            wav_path = self.audio_processor.process_audio_file(audio_file)
            if wav_path:
                logger.info(f"Audio processing completed: {wav_path}")
                self.step_results['audio_processing'] = {
                    'status': 'success',
                    'output_path': wav_path,
                    'input_file': audio_file
                }
                return wav_path
            else:
                logger.error("Audio processing failed")
                self.step_results['audio_processing'] = {
                    'status': 'failed',
                    'input_file': audio_file
                }
                return None
                
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            self.step_results['audio_processing'] = {
                'status': 'error',
                'error': str(e),
                'input_file': audio_file
            }
            return None
    
    def transcribe_audio_step(self, wav_path: str) -> Optional[Dict[str, Any]]:
        """
        Process audio file through the transcription step.
        
        Args:
            wav_path: Path to the WAV file to transcribe
            
        Returns:
            Optional[Dict[str, Any]]: Transcription result
        """
        logger.info(f"Step 2: Transcription - {wav_path}")
        
        try:
            transcription_result = self.transcription_engine.process_audio_file(wav_path)
            if transcription_result:
                logger.info("Transcription completed successfully")
                self.step_results['transcription'] = {
                    'status': 'success',
                    'text_length': len(transcription_result.get('text', '')),
                    'confidence_score': transcription_result.get('confidence_score', 0.0)
                }
                return transcription_result
            else:
                logger.error("Transcription failed")
                self.step_results['transcription'] = {
                    'status': 'failed',
                    'input_file': wav_path
                }
                return None
                
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            self.step_results['transcription'] = {
                'status': 'error',
                'error': str(e),
                'input_file': wav_path
            }
            return None
    
    def api_processing_step(self, transcription_text: str) -> Optional[Dict[str, Any]]:
        """
        Process transcribed text through the API step.
        
        Args:
            transcription_text: Transcribed text to process
            
        Returns:
            Optional[Dict[str, Any]]: API response
        """
        logger.info(f"Step 3: API Processing - {len(transcription_text)} characters")
        
        try:
            # Pass the current audio filename for unique output naming
            api_response = self.api_client.process_transcription(transcription_text, self.current_file)
            if api_response:
                logger.info("API processing completed successfully")
                self.step_results['api_processing'] = {
                    'status': 'success',
                    'response_length': len(api_response.get('generated_text', ''))
                }
                return api_response
            else:
                logger.error("API processing failed")
                self.step_results['api_processing'] = {
                    'status': 'failed',
                    'input_length': len(transcription_text)
                }
                return None
                
        except Exception as e:
            logger.error(f"API processing error: {e}")
            self.step_results['api_processing'] = {
                'status': 'error',
                'error': str(e),
                'input_length': len(transcription_text)
            }
            return None
    
    def save_pipeline_summary(self) -> bool:
        """
        Save pipeline execution summary with unique filename.
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            summary = {
                'pipeline_info': {
                    'start_time': self.pipeline_start_time.isoformat() if self.pipeline_start_time else None,
                    'end_time': datetime.now().isoformat(),
                    'duration_seconds': time.time() - self.pipeline_start_time.timestamp() if self.pipeline_start_time else None,
                    'input_file': self.current_file
                },
                'step_results': self.step_results,
                'overall_status': 'success' if all(
                    step.get('status') == 'success' 
                    for step in self.step_results.values()
                ) else 'failed'
            }
            
            # Generate unique summary filename based on input file
            if self.current_file:
                base_name = Path(self.current_file).stem
                summary_filename = f"{base_name}_pipeline_summary.json"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                summary_filename = f"pipeline_summary_{timestamp}.json"
            
            summary_path = self.output_dir / summary_filename
            import json
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Pipeline summary saved to: {summary_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save pipeline summary: {e}")
            return False
    
    def process_single_file(self, audio_file: str) -> bool:
        """
        Process a single audio file through the complete pipeline.
        
        Args:
            audio_file: Name of the audio file to process
            
        Returns:
            bool: True if pipeline completed successfully, False otherwise
        """
        self.current_file = audio_file
        self.pipeline_start_time = datetime.now()
        self.step_results = {}
        
        logger.info(f"Starting pipeline for file: {audio_file}")
        
        try:
            # Step 1: Audio Processing
            wav_path = self.process_audio_step(audio_file)
            if not wav_path:
                logger.error("Pipeline failed at audio processing step")
                return False
            
            # Step 2: Transcription
            transcription_result = self.transcribe_audio_step(wav_path)
            if not transcription_result:
                logger.error("Pipeline failed at transcription step")
                return False
            
            transcription_text = transcription_result.get('text', '')
            if not transcription_text.strip():
                logger.error("Transcription produced empty text")
                return False
            
            # Step 3: API Processing
            api_response = self.api_processing_step(transcription_text)
            if not api_response:
                logger.error("Pipeline failed at API processing step")
                return False
            
            # Save pipeline summary
            self.save_pipeline_summary()
            
            logger.info(f"Pipeline completed successfully for {audio_file}")
            return True
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            self.step_results['pipeline_error'] = {
                'status': 'error',
                'error': str(e)
            }
            self.save_pipeline_summary()
            return False
    
    def process_all_files(self) -> Dict[str, bool]:
        """
        Process all audio files in the input directory.
        
        Returns:
            Dict[str, bool]: Results for each file (filename -> success)
        """
        logger.info("Starting batch processing of all audio files")
        
        # Validate environment
        if not self.validate_environment():
            logger.error("Environment validation failed")
            return {}
        
        # Get all audio files
        audio_files = self.audio_processor.list_audio_files()
        results = {}
        
        for audio_file in audio_files:
            logger.info(f"Processing file: {audio_file}")
            success = self.process_single_file(audio_file)
            results[audio_file] = success
            
            if success:
                logger.info(f"Successfully processed: {audio_file}")
            else:
                logger.error(f"Failed to process: {audio_file}")
        
        # Log summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        logger.info(f"Batch processing completed. {successful}/{total} files processed successfully")
        
        return results


def main():
    """Main entry point for the pipeline."""
    pipeline = AudioTranscriptionPipeline()
    
    # Process all files
    results = pipeline.process_all_files()
    
    # Print results
    print("\nPipeline Results:")
    for filename, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{filename}: {status}")


if __name__ == "__main__":
    main() 