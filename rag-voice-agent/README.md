<!-- pip install livekit-agents livekit-plugins-assemblyai python-dotenv -->


# RAG Voice Agent

This project implements a RAG (Retrieval Augmented Generation) voice agent using LlamaIndex and LiveKit. It provides two different implementations:
1. `voice_agent_openai.py` - Using OpenAI for speech and language processing
2. `voice_agent.py` - Using AssemblyAI and Ollama (with Gemma) for speech and language processing

## Installation

Ensure you have Python 3.11 or later installed.

### Common Dependencies
```bash
pip install livekit-agents livekit-plugins python-dotenv llama-index-core
```

## Implementation 1: voice_agent_openai.py

This implementation uses OpenAI's services for speech-to-text and text-to-speech capabilities.

### Requirements
1. OpenAI API key
2. Cartesia AI key
3. LiveKit credentials

### Setup
1. Copy `.env.example` to `.env`
2. Configure the following environment variables:
```bash
OPENAI_API_KEY=your_openai_api_key
CARTESIA_API_KEY=your_cartesia_api_key
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

### Running
```bash
python voice_agent_openai.py
```

## Implementation 2: voice_agent.py

This implementation uses AssemblyAI for speech processing and Ollama (with Gemma) for language tasks.

### Requirements
1. AssemblyAI API key
2. Ollama installation (for Gemma 3B)
3. LiveKit credentials

### Setup

1. **Install Ollama**
   ```bash
   # For macOS
   brew install ollama
   
   # For Linux
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Pull Gemma Model**
   ```bash
   ollama pull gemma
   ```

3. **Configure Environment**
   Copy `.env.example` to `.env` and set:
   ```bash
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key
   LIVEKIT_URL=your_livekit_url
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   ```

### Running
1. Start Ollama server:
   ```bash
   ollama serve
   ```

2. In a new terminal, run the voice agent:
   ```bash
   python voice_agent.py
   ```

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

