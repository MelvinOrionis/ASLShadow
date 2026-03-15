import cv2
import time
import random
from app.overlay import draw_overlay

DEMO_WORDS = ["hello", "thank you", "yes", "no", "help",
              "stop", "please", "water", "more", "pain"]

def fake_predict():
    word = random.choice(DEMO_WORDS)
    confidence = round(random.uniform(0.72, 0.97), 2)
    return word, confidence

SMOOTHING_FRAMES = 8
PREDICT_INTERVAL = 0.5

def run_webcam(predict_fn=fake_predict):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("ERROR: Cannot open webcam. Try changing 0 to 1")
        return

    history          = []
    stable_word      = ""
    stable_conf      = 0.0
    last_predict_t   = 0
    word_history_log = []

    print("Shadow is live — press Q to quit, R to reset")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("ERROR: Frame read failed.")
            break

        frame = cv2.flip(frame, 1)

        now = time.time()
        if now - last_predict_t > PREDICT_INTERVAL:
            word, conf     = predict_fn()
            last_predict_t = now
            history.append(word)
            if len(history) > SMOOTHING_FRAMES:
                history.pop(0)

            if len(history) == SMOOTHING_FRAMES and history.count(history[-1]) >= 5:
                if history[-1] != stable_word:
                    stable_word = history[-1]
                    stable_conf = conf
                    word_history_log.append(stable_word)
                    if len(word_history_log) > 5:
                        word_history_log.pop(0)

        frame = draw_overlay(frame, stable_word, stable_conf,
                             True, word_history_log)

        cv2.imshow("Shadow — ASL Recognition", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('r'):
            history          = []
            stable_word      = ""
            stable_conf      = 0.0
            word_history_log = []

    cap.release()
    cv2.destroyAllWindows()
    print("Shadow closed.")

if __name__ == "__main__":
    run_webcam()
