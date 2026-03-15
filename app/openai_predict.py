import os
import base64
import cv2
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Setup OpenRouter Client
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

def encode_image_to_base64(frame):
    # Resize to 512px to keep it fast and cheap
    h, w = frame.shape[:2]
    scale = 512 / max(h, w)
    small = cv2.resize(frame, (int(w * scale), int(h * scale)))
    
    _, buffer = cv2.imencode(".jpg", small)
    return base64.b64encode(buffer).decode('utf-8')

def predict_and_expand(frame):
    # 1. CROP (Keep your existing crop logic)
    h, w = frame.shape[:2]
    box_w, box_h = 340, 380
    x1, y1 = (w - box_w) // 2, (h - box_h) // 2 - 30
    x2, y2 = x1 + box_w, y1 + box_h
    cropped = frame[max(0,y1):min(h,y2), max(0,x1):min(w,x2)]

    # 2. ENCODE
    base64_image = encode_image_to_base64(cropped)

    # 3. CALL OPENROUTER
    try:
        print("Sending to OpenRouter...")
        response = client.chat.completions.create(
            # You can swap models here: 
            # "google/gemini-flash-1.5"
            # "openai/gpt-4o-mini"
            # "meta-llama/llama-3.2-11b-vision-instruct" (Very fast!)
            model="openai/gpt-4o-mini", 
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Identify this ASL sign or gesture. Return EXACTLY: WORD|NATURAL SENTENCE|0.9. If nothing, return NONE|NONE|0.0"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )
        
        raw = response.choices[0].message.content.strip()
        print(f"AI Response: {raw}")
        
        if "NONE" in raw: return "", "", 0.0
        
        parts = raw.split("|")
        word = parts[0].strip().upper()
        sentence = parts[1].strip()
        conf = float(parts[2].strip()) if len(parts) > 2 else 0.90
        return word, sentence, conf

    except Exception as e:
        print(f"OpenRouter Error: {e}")
        return "ERROR", "Could not connect to AI.", 0.0
