"""
Gemini API Client Module

Handles communication with Google Gemini API:
- Sends transcribed text to Gemini API
- Uses specified endpoint and authentication
- Formats requests according to JSON specification
- Handles API rate limits and errors
- Implements retry logic and rate limiting
"""

import os
import logging
import requests
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except:
    pass  # Continue without .env file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiAPIClient:
    """Handles communication with Google Gemini API."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the Gemini API client.
        
        Args:
            output_dir: Directory for API response outputs
        """
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.api_url = os.getenv('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent')
        self.output_dir = Path(output_dir)
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
        # Rate limiting settings
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.rate_limit_delay = 2  # seconds between requests
        
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
        else:
            logger.info("Gemini API client initialized successfully")
    
    def validate_api_key(self) -> bool:
        """
        Validate the API key.
        
        Returns:
            bool: True if API key is valid, False otherwise
        """
        if not self.api_key:
            logger.error("API key is not set")
            return False
        
        if len(self.api_key) < 10:  # Basic validation
            logger.error("API key appears to be invalid (too short)")
            return False
        
        logger.info("API key validation passed")
        return True
    
    def format_request(self, text: str) -> Dict[str, Any]:
        """
        Format request according to Gemini API specification.
        
        Args:
            text: Transcribed text to send to API
            
        Returns:
            Dict[str, Any]: Formatted request payload
        """
        request_payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": text
                        }
                    ]
                }
            ]
        }
        
        logger.info(f"Request formatted for text length: {len(text)} characters")
        return request_payload
    
    def make_api_request(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Make API request to Gemini with retry logic.
        
        Args:
            text: Transcribed text to send
            
        Returns:
            Optional[Dict[str, Any]]: API response or None if failed
        """
        if not self.validate_api_key():
            return None
        
        request_payload = self.format_request(text)
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key  # <-- Use this instead of Authorization
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Making API request (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=request_payload,
                    timeout=30  # 30 second timeout
                )
                
                # Handle different response status codes
                if response.status_code == 200:
                    logger.info("API request successful")
                    return response.json()
                
                elif response.status_code == 429:  # Rate limited
                    logger.warning(f"Rate limited (attempt {attempt + 1}). Waiting {self.rate_limit_delay * (attempt + 1)} seconds...")
                    time.sleep(self.rate_limit_delay * (attempt + 1))
                    continue
                
                elif response.status_code == 401:  # Unauthorized
                    logger.error("API key is invalid or expired")
                    return None
                
                elif response.status_code == 400:  # Bad request
                    logger.error(f"Bad request: {response.text}")
                    return None
                
                else:
                    logger.error(f"API request failed with status {response.status_code}: {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return None
                
            except requests.exceptions.Timeout:
                logger.error(f"Request timeout (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None
        
        logger.error("All API request attempts failed")
        return None
    
    def parse_api_response(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse and validate API response.
        
        Args:
            response: Raw API response
            
        Returns:
            Optional[Dict[str, Any]]: Parsed response data
        """
        try:
            if not response:
                logger.error("Empty API response")
                return None
            
            # Extract the generated content
            candidates = response.get('candidates', [])
            if not candidates:
                logger.error("No candidates in API response")
                return None
            
            candidate = candidates[0]
            parts = candidate.get('content', {}).get('parts', [])
            
            if not parts:
                logger.error("No parts in API response")
                return None
            
            generated_text = parts[0].get('text', '')
            
            parsed_response = {
                'generated_text': generated_text,
                'response_metadata': {
                    'finish_reason': candidate.get('finishReason', ''),
                    'safety_ratings': candidate.get('safetyRatings', []),
                    'index': candidate.get('index', 0)
                },
                'usage_metadata': response.get('usageMetadata', {}),
                'prompt_feedback': response.get('promptFeedback', {})
            }
            
            logger.info(f"API response parsed successfully. Generated text length: {len(generated_text)} characters")
            return parsed_response
            
        except Exception as e:
            logger.error(f"Failed to parse API response: {e}")
            return None
    
    def save_api_response(self, response: Dict[str, Any], base_filename: str = "api_response") -> bool:
        """
        Save API response to file with unique filenames.
        
        Args:
            response: API response to save
            base_filename: Base filename for outputs (will be used to generate unique filenames)
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Generate unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save JSON response
            json_filename = f"{base_filename}_{timestamp}.json"
            output_path = self.output_dir / json_filename
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(response, f, indent=2, ensure_ascii=False)
            
            # Save plain text response
            txt_filename = f"{base_filename}_{timestamp}.txt"
            txt_path = self.output_dir / txt_filename
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(response.get('generated_text', ''))
            
            logger.info(f"API response saved to: {output_path} and {txt_path}")
            return True
            
            logger.info(f"API response saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save API response: {e}")
            return False
    
    def process_transcription(self, transcription_text: str, audio_filename: str = None) -> Optional[Dict[str, Any]]:
        """
        Process transcribed text through Gemini API.
        
        Args:
            transcription_text: Transcribed text to process
            audio_filename: Original audio filename for unique output naming
            
        Returns:
            Optional[Dict[str, Any]]: API response data
        """
        logger.info(f"Processing transcription through Gemini API (length: {len(transcription_text)} characters)")
        
        # Make API request
        api_response = self.make_api_request(transcription_text)
        if not api_response:
            logger.error("API request failed")
            return None
        
        # Parse response
        parsed_response = self.parse_api_response(api_response)
        if not parsed_response:
            logger.error("Failed to parse API response")
            return None
        
        # Save response with unique filename
        base_filename = f"{Path(audio_filename).stem}_api_response" if audio_filename else "api_response"
        if not self.save_api_response(parsed_response, base_filename):
            logger.error("Failed to save API response")
            return None
        
        logger.info("API processing completed successfully")
        return parsed_response


def main():
    """Test the Gemini API client."""
    client = GeminiAPIClient()
    
    # Test with sample text
    test_text = "This is a test transcription from Tamil audio."
    
    result = client.process_transcription(test_text)
    if result:
        print(f"API processing successful: {result['generated_text'][:100]}...")
    else:
        print("API processing failed")


if __name__ == "__main__":
    main()