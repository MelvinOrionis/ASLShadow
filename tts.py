import os
import io
import pygame
from dotenv import load_dotenv
from google import genai
from elevenlabs.client import ElevenLabs

load_dotenv()

gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
pygame.mixer.init()

def expand_word(word: str) -> str:
    response = gemini.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Turn this single ASL word into one natural spoken sentence a patient would say in a healthcare setting: {word}"
    )
    return response.text

def speak(text: str) -> None:
    expanded = expand_word(text)
    print(f"Speaking: {expanded}")
    audio = elevenlabs.text_to_speech.convert(
        text=expanded,
        voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
        model_id="eleven_flash_v2_5"
    )
    audio_data = b"".join(audio)
    pygame.mixer.music.load(io.BytesIO(audio_data))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

speak("HELP")
speak("PAIN")
speak("WATER")
