import cv2
import time
import random
import threading
from app.overlay import draw_overlay
from app.gemini_predict import predict_asl, predict_gesture

# ── Demo fallbacks ─────────────────────────────────────────────
DEMO_WORDS = ["hello", "thank you", "yes", "no", "help",
              "stop", "please", "water", "more", "pain"]
DEMO_GESTURES = ["volume up", "volume down", "play/pause",
                 "next slide", "prev slide", "screenshot"]

def fake_predict(frame=None):
    words = DEMO_WORDS if current_mode == MODE_ASL else DEMO_GESTURES
    return random.choice(words), round(random.uniform(0.72, 0.97), 2)

# ── Settings ───────────────────────────────────────────────────
MODE_ASL      = 1
MODE_GESTURE  = 2
PREDICT_INTERVAL = 4.1
SMOOTHING_FRAMES = 8

# ── Shared state ───────────────────────────────────────────────
current_mode   = MODE_ASL
latest_result  = {"word": "", "conf": 0.0}
predict_lock   = threading.Lock()
is_predicting  = False   # prevents overlapping Gemini calls
frozen         = False

# ── Async Gemini caller ────────────────────────────────────────
def run_predict_async(frame, mode):
    global is_predicting
    try:
        if mode == MODE_ASL:
            word, conf = predict_asl(frame)
        else:
            word, conf = predict_gesture(frame)
        with predict_lock:
            latest_result["word"] = word
            latest_result["conf"] = conf
    except Exception as e:
        print(f"Predict thread error: {e}")
    finally:
        is_predicting = False

# ── Main loop ──────────────────────────────────────────────────
def run_webcam():
    global current_mode, frozen, is_predicting

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    last_predict_t = 0.0
    history        = []
    stable_word    = ""
    stable_conf    = 0.0

    print("Shadow is live — 1=ASL  2=Gesture  SPACE=freeze  R=reset  Q=quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        now   = time.time()

        # ── Trigger async prediction ───────────────────────────
        if not frozen and not is_predicting and (now - last_predict_t > PREDICT_INTERVAL):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if gray.mean() > 30:
                is_predicting  = True
                last_predict_t = now
                t = threading.Thread(
                    target=run_predict_async,
                    args=(frame.copy(), current_mode),
                    daemon=True
                )
                t.start()

        # ── Read latest result (thread-safe) ───────────────────
        if not frozen:
            with predict_lock:
                word = latest_result["word"]
                conf = latest_result["conf"]

            if word:
                history.append((word, conf))
                if len(history) > SMOOTHING_FRAMES:
                    history.pop(0)

            if len(history) >= 3:
                counts = {}
                for w, c in history:
                    counts[w] = counts.get(w, []) + [c]
                best = max(counts, key=lambda w: len(counts[w]))
                if len(counts[best]) >= 3:
                    stable_word = best
                    stable_conf = round(sum(counts[best]) / len(counts[best]), 2)

        # ── Draw overlay ───────────────────────────────────────
        frame = draw_overlay(frame, stable_word, stable_conf,
                             mode=current_mode, frozen=frozen)

        cv2.imshow("Shadow", frame)

        # ── Key handling ───────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('1'):
            current_mode = MODE_ASL
            history.clear()
        elif key == ord('2'):
            current_mode = MODE_GESTURE
            history.clear()
        elif key == ord('r'):
            history.clear()
            stable_word = ""
            stable_conf = 0.0
            frozen      = False
            with predict_lock:
                latest_result["word"] = ""
                latest_result["conf"] = 0.0
        elif key == ord(' '):
            frozen = not frozen

    cap.release()
    cv2.destroyAllWindows()
    print("Shadow closed.")

if __name__ == "__main__":
    run_webcam()
