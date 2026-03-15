import time
import itertools
from PIL import Image
import io
from google import genai

# ── API Keys (add more keys to rotate if you have them) ────────
API_KEYS = [
    "paste-your-api-key-here",
    # "second-key-here",   ← add teammates' keys for more quota
]

key_cycle = itertools.cycle(API_KEYS)

# ── Backoff state ──────────────────────────────────────────────
_backoff_until = 0.0
_BACKOFF_SECONDS = 65  # wait 65s after a 429 before retrying

# ── Helper: get a fresh client ─────────────────────────────────
def get_client():
    return genai.Client(api_key=next(key_cycle))

# ── Helper: convert OpenCV frame → PIL Image ───────────────────
def frame_to_pil(frame):
    import cv2
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)

# ── Helper: resize image to save tokens ───────────────────────
def resize_for_api(pil_img, max_side=512):
    w, h  = pil_img.size
    scale = min(max_side / w, max_side / h, 1.0)
    if scale < 1.0:
        pil_img = pil_img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return pil_img

# ── Core API caller ────────────────────────────────────────────
def _call_gemini(prompt, frame):
    global _backoff_until

    # Still in backoff window — skip silently
    if time.time() < _backoff_until:
        remaining = int(_backoff_until - time.time())
        print(f"Gemini skipped — quota backoff {remaining}s remaining")
        return None

    try:
        pil_img = resize_for_api(frame_to_pil(frame))
        client  = get_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[pil_img, prompt]
        )
        return response.text.strip()

    except Exception as e:
        err = str(e)
        if "429" in err or "RESOURCE_EXHAUSTED" in err:
            _backoff_until = time.time() + _BACKOFF_SECONDS
            print(f"Gemini quota hit — backing off for {_BACKOFF_SECONDS}s")
        else:
            print(f"Gemini error: {e}")
        return None

# ── Public functions ───────────────────────────────────────────
def predict_asl(frame):
    """
    Takes an OpenCV BGR frame, returns (word, confidence) for ASL detection.
    """
    prompt = (
        "Look at the hand in this image. "
        "What single ASL word or letter is being signed? "
        "Reply with ONLY the word and a confidence score 0.0-1.0, "
        "comma-separated. Example: hello,0.92 "
        "If no hand is visible reply: none,0.0"
    )
    result = _call_gemini(prompt, frame)
    return _parse_result(result)

def predict_gesture(frame):
    """
    Takes an OpenCV BGR frame, returns (gesture, confidence) for gesture detection.
    """
    prompt = (
        "Look at the hand gesture in this image. "
        "What control gesture is being made? Choose from: "
        "volume up, volume down, play/pause, next slide, prev slide, screenshot. "
        "Reply with ONLY the gesture name and a confidence score 0.0-1.0, "
        "comma-separated. Example: volume up,0.88 "
        "If no hand is visible reply: none,0.0"
    )
    result = _call_gemini(prompt, frame)
    return _parse_result(result)

# ── Parser ─────────────────────────────────────────────────────
def _parse_result(raw):
    """Parse 'word,0.92' into ('word', 0.92). Returns ('', 0.0) on failure."""
    if not raw:
        return ("", 0.0)
    try:
        parts = raw.strip().split(",")
        word  = parts[0].strip().lower()
        conf  = float(parts[1].strip()) if len(parts) > 1 else 0.75
        if word == "none":
            return ("", 0.0)
        return (word, round(conf, 2))
    except Exception:
        # If Gemini returns something unexpected, try to salvage just the word
        word = raw.strip().lower().split()[0] if raw.strip() else ""
        return (word, 0.75) if word and word != "none" else ("", 0.0)
