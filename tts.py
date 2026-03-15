import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import pygame
import io

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
pygame.mixer.init()

def speak(text: str) -> None:
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
        model_id="eleven_flash_v2_5"
    )
    audio_data = b"".join(audio)
    pygame.mixer.music.load(io.BytesIO(audio_data))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

