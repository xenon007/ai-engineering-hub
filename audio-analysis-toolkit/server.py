from mcp.server.fastmcp import FastMCP
import assemblyai as aai
import os
from typing import Any, Dict, List
from dotenv import load_dotenv

load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

mcp = FastMCP("AssemblyAI Audio Analysis")
_last_transcript: aai.Transcript = None


def _format_timestamp(ms: int) -> str:
    # Convert milliseconds to HH:MM:SS
    seconds_total = ms // 1000
    hours = seconds_total // 3600
    minutes = (seconds_total % 3600) // 60
    seconds = seconds_total % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

@mcp.tool()
def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe audio and return sentences with timestamps (HH:MM:SS).
    Caches the Transcript object for later queries.
    """
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        iab_categories=True,
        speakers_expected=2,
        sentiment_analysis=True,
        summarization=True,
        language_detection=True
    )
    transcript = aai.Transcriber().transcribe(audio_path, config=config)
    sentences = transcript.get_sentences()
    serialized: List[Dict[str, Any]] = [
        {"timestamp": _format_timestamp(s.start), "text": s.text}
        for s in sentences
    ]
    global _last_transcript
    _last_transcript = transcript
    return {"sentences": serialized}

@mcp.tool()
def get_audio_data(
    text: bool = False,
    timestamps: bool = False,
    summary: bool = False,
    speakers: bool = False,
    sentiment: bool = False,
    topics: bool = False
) -> dict:
    """
    Retrieve features from the last transcript.

    Flags:
        text: full transcript text
        timestamps: timestamped sentences
        summary: summary
        speakers: speaker labels
        sentiment: sentiment analysis
        topics: topic categories
    """
    transcript = _last_transcript
    if transcript is None:
        return {"error": "No transcript available. Please run transcribe_audio first."}

    out: Dict[str, Any] = {}
    if text:
        out["text"] = " ".join(s.text for s in transcript.get_sentences())
    if timestamps:
        out["sentences"] = [
            {"timestamp": _format_timestamp(s.start), "text": s.text}
            for s in transcript.get_sentences()
        ]
    if summary:
        out["summary"] = transcript.summary
    if speakers:
        out["speakers"] = [
            {
                "speaker": u.speaker,
                "timestamp": _format_timestamp(u.start),
                "text": u.text
            }
            for u in transcript.utterances
        ]
    if sentiment:
        sl = transcript.sentiment_analysis
        counts = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
        details = []
        for s in sl:
            counts[s.sentiment] += 1
            details.append({
                "timestamp": _format_timestamp(s.start),
                "speaker": s.speaker,
                "text": s.text,
                "sentiment": s.sentiment
            })
        out["sentiment"] = {"counts": counts, "details": details}
    if topics:
        out["topics"] = transcript.iab_categories.summary

    return out

if __name__ == "__main__":
    mcp.run()
