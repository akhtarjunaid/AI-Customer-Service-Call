from openai import OpenAI
import os

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


def transcribe_with_whisper(audio_file):
    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )

    return transcription.text
