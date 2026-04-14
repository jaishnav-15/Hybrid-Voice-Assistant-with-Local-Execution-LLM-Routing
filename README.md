## Hybrid-Voice-Assistant-with-Local-Execution-LLM-Routing
Real-time voice assistant using wake word detection, Whisper ASR, hybrid command routing, Groq LLM, and TTS for fast intelligent responses


## Overview

This project implements a complete voice pipeline that listens for a wake word, captures user speech, converts it to text, and intelligently decides whether to execute a local command or query a language model.

The system is designed to reduce latency by prioritizing local execution while still supporting complex queries through an LLM.

---

## Features

- Wake word activation ("computer")
- Real-time speech-to-text using Whisper
- Hybrid command routing (local + LLM)
- Local system automation (apps, folders, web)
- Short-term conversational memory
- Text-to-speech output
- Latency monitoring for performance analysis

---

## Architecture

The system follows this pipeline:

1. Wake word detection (Porcupine)
2. Audio capture
3. Speech-to-text (Whisper)
4. Command routing
5. Local execution or LLM processing
6. Response generation
7. Text-to-speech output

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/voice-ai-assistant.git
cd voice-ai-assistant
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file and add:

```env
PICOVOICE_ACCESS_KEY=your_key_here
GROQ_API_KEY=your_key_here
WAKE_WORD=computer
```

---

## Usage

Run the application:

```bash
python wakenew_github.py
```

Say the wake word ("computer") followed by a command.

---

## Example Commands

- Open YouTube  
- Search for machine learning projects  
- What time is it  
- Open downloads  
- Who are you  

---

## How It Works

### Wake Word Detection
Continuously listens and activates when the wake word is detected.

### Speech Recognition
Audio is converted to text using Whisper.

### Command Routing
- Local commands → executed directly  
- Other queries → sent to LLM  

### Local Execution
Supports:
- Opening applications  
- Accessing folders  
- Web browsing  
- System control  

### LLM Processing
Uses Groq API and maintains short conversation context.

### Text-to-Speech
Responses are spoken using the system TTS engine.

---

## Project Structure

```
voice-ai-assistant/
│
├── wakenew_github.py
├── README.md
├── requirements.txt
├── .env.example
├── assets/
│   └── architecture.png
```

---

## Tech Stack

- Python  
- Whisper (faster-whisper)  
- Porcupine  
- Groq API  
- SoundDevice  
- System TTS  

---

## Performance

The system tracks:
- Transcription time  
- Routing time  
- LLM response time  
- Total latency  

---

## Limitations

- Optimized for Windows (TTS and system commands)  
- Requires microphone access  
- Depends on external API for LLM  

---

## Future Improvements

- Add RAG (retrieval-based responses)  
- Long-term memory (vector database)  
- Cross-platform support  
- GUI interface  
- Multi-language support  

---


