"""OpenAI Whisper API integration with automatic language detection."""

import io
from openai import OpenAI


def transcribe(audio_bytes: bytes, api_key: str) -> str:
    """Transcribes audio bytes using OpenAI Whisper.

    Args:
        audio_bytes: WAV file as bytes.
        api_key: OpenAI API key.

    Returns:
        Transcribed text.

    Raises:
        Exception: On API or network errors.
    """
    client = OpenAI(api_key=api_key)

    # BytesIO with filename -- the OpenAI SDK requires a file-like object
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "recording.wav"

    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        # No language parameter -> automatic language detection
        # Whisper handles code-switching (e.g. German + English) natively
    )

    return response.text.strip()
