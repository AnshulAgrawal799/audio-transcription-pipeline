#!/usr/bin/env python3
"""
Main Entry Point for Audio Transcription & Translation Pipeline

This script provides a simple command-line interface for the complete pipeline
that processes Tamil audio files, transcribes them to English, and sends the
results to Google's Gemini API for further processing.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import AudioTranscriptionPipeline


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pipeline.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main entry point for the audio transcription pipeline."""
    parser = argparse.ArgumentParser(
        description="Audio Transcription & Translation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Process all audio files in audio/ directory
  python main.py --file audio2.mp3  # Process specific file
  python main.py --verbose          # Enable verbose logging
  python main.py --help             # Show this help message
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Specific audio file to process (e.g., audio2.mp3)'
    )
    
    parser.add_argument(
        '--input-dir', '-i',
        type=str,
        default='audio',
        help='Input directory containing audio files (default: audio)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='output',
        help='Output directory for results (default: output)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Audio Transcription Pipeline v1.0'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Print welcome message
    print("🎵 Audio Transcription & Translation Pipeline")
    print("=" * 50)
    print("Processing Tamil audio files to English text with Gemini API integration")
    print()
    
    try:
        # Initialize pipeline
        pipeline = AudioTranscriptionPipeline(
            input_dir=args.input_dir,
            output_dir=args.output_dir
        )
        
        # Process files
        if args.file:
            # Process specific file
            logger.info(f"Processing specific file: {args.file}")
            
            # Check if file exists
            file_path = Path(args.input_dir) / args.file
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                print(f"❌ Error: File not found - {file_path}")
                return 1
            
            # Process single file
            success = pipeline.process_single_file(args.file)
            
            if success:
                print(f"✅ Successfully processed: {args.file}")
                print(f"📁 Results saved in: {args.output_dir}")
                return 0
            else:
                print(f"❌ Failed to process: {args.file}")
                return 1
        
        else:
            # Process all files
            logger.info("Processing all audio files in input directory")
            
            # Validate environment first
            if not pipeline.validate_environment():
                print("❌ Environment validation failed")
                print("Please check:")
                print("  - Input directory exists and contains MP3 files")
                print("  - GEMINI_API_KEY is set in .env file")
                print("  - FFmpeg is installed and accessible")
                return 1
            
            # Process all files
            results = pipeline.process_all_files()
            
            # Print results summary
            print("\n📊 Processing Results:")
            print("-" * 30)
            
            successful = 0
            total = len(results)
            
            for filename, success in results.items():
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"{filename}: {status}")
                if success:
                    successful += 1
            
            print("-" * 30)
            print(f"Total files: {total}")
            print(f"Successful: {successful}")
            print(f"Failed: {total - successful}")
            
            if successful > 0:
                print(f"\n📁 Results saved in: {args.output_dir}")
                print("Files generated for each audio file:")
                print("  - {audio_name}_converted.wav (converted audio)")
                print("  - {audio_name}_transcription.txt (plain text transcription)")
                print("  - {audio_name}_transcription_detailed.json (detailed transcription data)")
                print("  - {audio_name}_api_response_YYYYMMDD_HHMMSS.json (Gemini API response)")
                print("  - {audio_name}_api_response_YYYYMMDD_HHMMSS.txt (API response text)")
                print("  - {audio_name}_pipeline_summary.json (execution summary)")
                print("  - pipeline.log (detailed execution log)")
            
            return 0 if successful == total else 1
    
    except KeyboardInterrupt:
        print("\n⚠️  Pipeline interrupted by user")
        return 1
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())