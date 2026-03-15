import os
import io
import pygame
import pyttsx3 # Install this: pip install pyttsx3
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

# SET THIS TO FALSE TO SAVE CREDITS DURING TESTING
USE_ELEVENLABS = False 

engine = pyttsx3.init()
elevenlabs = None
if USE_ELEVENLABS:
    elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

pygame.mixer.init()

def speak(text: str) -> None:
    if not text: return
    print(f"Shadow speaking: {text}")

    if not USE_ELEVENLABS:
        # USE FREE SYSTEM VOICE
        engine.say(text)
        engine.runAndWait()
    else:
        # USE ELEVENLABS
        try:
            audio = elevenlabs.text_to_speech.convert(
                text=text,
                voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
                model_id="eleven_flash_v2_5"
            )
            audio_data = b"".join(audio)
            pygame.mixer.music.load(io.BytesIO(audio_data))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"ElevenLabs Error: {e}")
