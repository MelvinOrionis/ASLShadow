import sys
import os
import time
import threading
import cv2

# Fix Paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from app.overlay import draw_overlay
from app.openai_predict import predict_and_expand
from tts import speak

# State
latest_result = {"word": "", "sentence": "", "conf": 0.0}
is_predicting = False
predict_lock = threading.Lock()

def run_predict_async(frame):
    global is_predicting, latest_result
    try:
        # We call the API once
        word, sentence, conf = predict_and_expand(frame)
        
        # User requested: Take the best guess regardless of confidence
        if word:
            with predict_lock:
                latest_result["word"] = word
                latest_result["sentence"] = sentence
                latest_result["conf"] = conf
            
            # Speak the expansion
            speak(sentence)
    except Exception as e:
        print(f"Prediction Error: {e}")
    finally:
        is_predicting = False

def run_webcam():
    global is_predicting, latest_result
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return

    print("\n--- AslShadow: Manual Mode ---")
    print("1. Hold your sign in the box.")
    print("2. Press 'S' to Capture & Translate.")
    print("3. Press 'Q' to Quit.")

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)

        # UI Overlay logic
        with predict_lock:
            word = latest_result["word"]
            conf = latest_result["conf"]
        
        # Draw the standard UI
        processed_frame = draw_overlay(frame, word, conf)
        
        # Add Manual Mode Instructions to screen
        if is_predicting:
            msg = "ANALYZING... PLEASE WAIT"
            col = (0, 255, 255) # Yellow
        else:
            msg = "READY: PRESS 'S' TO SCAN"
            col = (0, 255, 0) # Green
            
        cv2.putText(processed_frame, msg, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, col, 2)

        cv2.imshow("AslShadow", processed_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        
        # MANUAL TRIGGER
        elif key == ord('s'):
            if not is_predicting:
                print("Snapshot taken! Sending to Gemini...")
                is_predicting = True
                # Pass a copy of the CURRENT frame to the thread
                threading.Thread(target=run_predict_async, args=(frame.copy(),), daemon=True).start()
            else:
                print("Still processing previous request...")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_webcam()
