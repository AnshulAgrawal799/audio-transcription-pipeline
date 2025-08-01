# Audio processing constants
SAMPLE_RATE = 16000
CHANNELS = 1
MAX_FILE_SIZE_MB = 50
SUPPORTED_AUDIO_EXTENSIONS = ['.mp3']

# Transcription output patterns
TRANSCRIPTION_TXT_PATTERN = "{audio_name}_transcription.txt"
TRANSCRIPTION_JSON_PATTERN = "{audio_name}_transcription_detailed.json"

# Translation output patterns
TRANSLATION_TXT_PATTERN = "{audio_name}_translation.txt"
TRANSLATION_JSON_PATTERN = "{audio_name}_translation_detailed.json"

# TTS output patterns
TTS_AUDIO_PATTERN = "{base_filename}_{timestamp}.mp3"
TTS_METADATA_PATTERN = "{base_filename}_metadata.json"

# (Optional) Add more patterns for API responses, summaries, etc.
# API_RESPONSE_JSON_PATTERN = "{audio_name}_api_response_{timestamp}.json"
# PIPELINE_SUMMARY_PATTERN = "{audio_name}_pipeline_summary.json"