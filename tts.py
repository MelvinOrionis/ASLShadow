import os
import io
import pygame
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

# --- THE FIX: Set this to True for the high-quality voice ---
USE_ELEVENLABS = True 

elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
pygame.mixer.init()

def speak(text: str) -> None:
    if not text: return
    print(f"Shadow speaking: {text}")

    if not USE_ELEVENLABS:
        # Fallback to system voice if needed
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    else:
        try:
            # This uses the "good" voice from your .env
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
            print(f"ElevenLabs Error: {e}. Falling back to system voice.")
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
