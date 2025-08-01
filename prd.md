# Product Requirements Document (PRD)  
## Audio Transcription & Tamil Voice Translation Pipeline with Gemini API Integration  

**Project:** Audio-to-Text-to-Voice Translation Pipeline  
**Version:** 1.3  
**Date:** August 2025  
**Status:** In Development  

---

## 📋 Executive Summary

This project implements a complete local Python pipeline that processes Tamil audio files, transcribes them to English text using OpenAI's Whisper, translates the English to Tamil using Google Translate (via `googletrans`), and finally converts the Tamil text to natural Tamil speech using gTTS (Google Text-to-Speech).

---

## 🎯 Project Objectives

### Primary Goals
- Create a seamless audio-to-voice translation pipeline
- Integrate OpenAI Whisper for accurate Tamil-to-English transcription
- Use `googletrans` for English-to-Tamil translation
- Use `gTTS` for Tamil voice synthesis
- Ensure local deployment without heavy system requirements

### Success Metrics
- Audio transcription accuracy > 90%
- Pipeline execution time < 5 minutes for standard audio files
- Natural-sounding Tamil voice generation
- Cross-platform compatibility (Windows, macOS, Linux)

---

## 🏗️ Technical Architecture

### System Components
1. **Audio Processing Module** – Handles MP3 to WAV conversion  
2. **Transcription Engine** – OpenAI Whisper integration  
3. **Translation Layer** – English to Tamil translation using `googletrans`  
4. **TTS Layer** – Tamil text to speech using `gTTS`  
5. **Pipeline Orchestrator** – Coordinates all components  

### Technology Stack
- **Language:** Python 3.8+  
- **Audio Processing:** FFmpeg, OpenAI Whisper  
- **Translation:** `googletrans`  
- **Text-to-Speech:** `gTTS`  
- **Dependencies:** requests, pydub, whisper, gtts, googletrans  

---

## 📝 Detailed Requirements

### Functional Requirements

#### FR-001: Audio Input and Preprocessing
- Accepts `.mp3` or `.wav` audio input  
- Converts to 16kHz mono WAV format  
- Uses `pydub` and `ffmpeg` for conversion  

#### FR-002: Tamil-to-English Transcription with Whisper
- Uses Whisper to transcribe Tamil audio to English text  
- Model: `base` or `small`  
- Runs on CPU with `fp16=False`  

#### FR-003: Output Formatting
- Outputs English text as plain `.txt` file  
- Supports chunked or full transcript export  

#### FR-004: English-to-Tamil Translation
- Uses `googletrans`  
- Translates English transcription output to Tamil  
- Handles long and multi-line inputs  
- Provides fallback on failure  
- See "Sample Output Files" for output format details.

#### FR-005: Tamil Text-to-Speech with gTTS
- Uses `gTTS` for Tamil voice generation  
- Converts UTF-8 Tamil text into natural speech  
- Saves output as MP3 or WAV  
- Supports language code `ta`  
- See "Technical Specifications" for example code.

#### FR-006: Pipeline Orchestration
- Manages sequential execution: Audio → Transcription → Translation → TTS  
- CLI or Python script entry point (e.g., `main.py`)  
- Provides clear logs at each step (see "Logging Format")  
- Returns final Tamil MP3 file path  

---

### Non-Functional Requirements

#### NFR-002: Cross-Platform Compatibility
- Script runs on Windows, Linux, and macOS  
- Tested using virtual environments or Docker  

#### NFR-003: Minimal Latency and Memory Usage
- Total execution time < 5 minutes for a 2-minute audio  
- Memory footprint ≤ 1.5 GB on CPU systems  

---

## 📁 Sample Output Files

| Stage        | File Name        | Format      | Example                              |
|--------------|------------------|-------------|--------------------------------------|
| Transcription| `output_en.txt`  | Plain text  | "You're describing a new process..." |
| Translation  | `output_ta.txt`  | UTF-8 Tamil | "நீங்கள் ஒரு புதிய முடிவு செய்கிறீர்கள்..." |
| TTS Audio    | `output_tamil.mp3` | MP3 audio | Playable on standard media players   |

---

## 📟 Logging Format

### Text Log Output (Standard)
```
[INFO] Step 1: Audio converted to WAV (duration: 00:01:59)
[INFO] Step 2: Transcription completed. Output saved to output_en.txt
[INFO] Step 3: Translation completed. Output saved to output_ta.txt
[INFO] Step 4: TTS completed. Audio saved as output_tamil.mp3
```

### Optional JSON Log Format
```json
{
  "step": "Transcription",
  "status": "success",
  "output_file": "output_en.txt",
  "duration_seconds": 44.8
}
```

---

## 🎯 Jira-Style Task Management

### Sprint 2: Translation and Voice Generation
**Duration:** 1 Day  
**Goal:** Implement Google Translate and gTTS integration

##### Story: PROJ-004 - English-to-Tamil Translation with googletrans
- [x] Install and configure `googletrans`  
- [x] Translate English to Tamil  
- [x] Validate translation quality  
- [x] Handle translation exceptions and fallbacks  

##### Story: PROJ-005 - Tamil TTS with gTTS
- [x] Install `gTTS`  
- [x] Convert Tamil text to MP3 or WAV  
- [x] Validate pronunciation and audio clarity  
- [x] Save audio file and provide path for playback  

---

## 🚀 Implementation Timeline

| Sprint   | Duration | Focus Area           | Key Deliverables                            |
|----------|----------|----------------------|---------------------------------------------|
| Sprint 1 | Day 1    | Foundation            | Project structure, audio processing, Whisper setup |
| Sprint 2 | Day 2    | Translation & TTS     | googletrans + gTTS integration              |
| Sprint 3 | Day 3    | Pipeline              | Integration, testing, validation            |
| Sprint 4 | Day 4    | Documentation         | Final README, deployment scripts            |

---

## 🛠️ Technical Specifications

### Translation & TTS Example Code
```python
from googletrans import Translator
from gtts import gTTS

# Translate English → Tamil
translator = Translator()
tamil_text = translator.translate("You're describing a new process...", src='en', dest='ta').text

# Convert Tamil text to speech
tts = gTTS(text=tamil_text, lang='ta')
tts.save("tamil_output.mp3")
```

### Configuration Requirements
- **Whisper Model:** `base`  
- **Audio Format:** WAV, 16kHz, Mono  
- **CPU Mode:** `fp16=False`  
- **TTS Engine:** `gTTS` with lang='ta'  

### Dependencies
```
openai-whisper @ git+https://github.com/openai/whisper.git
requests>=2.25.1
pydub>=0.25.1
ffmpeg-python>=0.2.0
gtts>=2.2.3
googletrans==4.0.0-rc1
```

---

## 🧪 Testing Strategy

### Unit Testing
- Validate translation strings against expected output  
- Check if audio files are generated, saved, and playable  

### Integration Testing
- Run full pipeline with sample Tamil audio  
- Assert correct outputs at each stage  

### User Acceptance Testing
- Use native speakers to validate pronunciation, translation accuracy, and clarity  

---

## 📊 Success Metrics

- **Translation Accuracy:** > 85% (BLEU or manual eval)  
- **Voice Clarity:** > 4.5/5 by native speakers  
- **Pipeline Speed:** < 5 minutes for a 2-minute audio  
- **Reliability:** > 95% success rate over repeated runs  

---

## 🔄 Risk Management

| Risk                          | Probability | Impact | Mitigation                                     |
|-------------------------------|-------------|--------|------------------------------------------------|
| gTTS Tamil pronunciation gaps | Low         | Medium | Try Coqui or edge-tts as fallback              |
| Google Translate limits       | Medium      | Medium | Add retries, rate-limiting, or offline caching |

---

## 📋 Definition of Done

- [x] Tamil MP3 speech is generated from input audio  
- [x] Logs are printed for each major pipeline stage  
- [x] Intermediate `.txt` and final `.mp3` files saved  
- [x] Confirmed working on at least Windows and Linux  

---

**Document Version:** 1.3  
**Last Updated:** August 2025
