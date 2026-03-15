import cv2

FONT      = cv2.FONT_HERSHEY_SIMPLEX
GREEN     = (0,  220, 100)
BLUE      = (255, 180,  50)
ORANGE    = (0,  180, 255)
WHITE     = (255, 255, 255)
DARK_GREY = (30,  30,  30)
MID_GREY  = (120, 120, 120)

MODE_ASL     = 1
MODE_GESTURE = 2

def draw_guide_box(frame, word, mode, frozen):
    h, w  = frame.shape[:2]
    box_w, box_h = 340, 380
    x1 = (w - box_w) // 2
    y1 = (h - box_h) // 2 - 30
    x2 = x1 + box_w
    y2 = y1 + box_h
    if frozen:
        color = BLUE
    elif word:
        color = GREEN
    else:
        color = ORANGE
    thickness = 2
    cl = 30
    cv2.line(frame, (x1, y1), (x1 + cl, y1), color, thickness)
    cv2.line(frame, (x1, y1), (x1, y1 + cl), color, thickness)
    cv2.line(frame, (x2, y1), (x2 - cl, y1), color, thickness)
    cv2.line(frame, (x2, y1), (x2, y1 + cl), color, thickness)
    cv2.line(frame, (x1, y2), (x1 + cl, y2), color, thickness)
    cv2.line(frame, (x1, y2), (x1, y2 - cl), color, thickness)
    cv2.line(frame, (x2, y2), (x2 - cl, y2), color, thickness)
    cv2.line(frame, (x2, y2), (x2, y2 - cl), color, thickness)
    if frozen:
        label = "FROZEN"
    elif word:
        label = "SIGNING"
    else:
        label = "Place hand here"
    (tw, _), _ = cv2.getTextSize(label, FONT, 0.55, 1)
    cv2.putText(frame, label, ((w - tw) // 2, y1 - 10), FONT, 0.55, color, 1)
    return frame

def draw_overlay(frame, word, confidence, mode=1, frozen=False):
    h, w = frame.shape[:2]
    frame = draw_guide_box(frame, word, mode, frozen)
    bar = frame.copy()
    cv2.rectangle(bar, (0, h - 140), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(bar, 0.55, frame, 0.45, 0, frame)
    mode_label = "[ ASL MODE ]" if mode == MODE_ASL else "[ GESTURE MODE ]"
    mode_color = GREEN if mode == MODE_ASL else BLUE
    (tw, _), _ = cv2.getTextSize(mode_label, FONT, 0.55, 1)
    cv2.putText(frame, mode_label, ((w - tw) // 2, 28), FONT, 0.55, mode_color, 1)
    cv2.putText(frame, "Shadow", (w - 130, 32), FONT, 0.9, WHITE, 2)
    dot_color = BLUE if frozen else (GREEN if word else ORANGE)
    status = "FROZEN" if frozen else ("Detected" if word else "Waiting...")
    cv2.circle(frame, (22, 22), 9, dot_color, -1)
    cv2.putText(frame, status, (38, 28), FONT, 0.6, dot_color, 2)
    if word:
        display = word.upper()
        scale, thick = 2.8, 5
        (tw, _), _ = cv2.getTextSize(display, FONT, scale, thick)
        cv2.putText(frame, display, ((w - tw) // 2, h - 70), FONT, scale, WHITE, thick)
        bar_len  = 260
        bar_x    = (w - bar_len) // 2
        bar_fill = int(confidence * bar_len)
        bar_col  = GREEN if confidence >= 0.80 else ORANGE
        cv2.rectangle(frame, (bar_x, h - 42), (bar_x + bar_len, h - 26), DARK_GREY, -1)
        cv2.rectangle(frame, (bar_x, h - 42), (bar_x + bar_fill, h - 26), bar_col, -1)
        cv2.putText(frame, f"{int(confidence * 100)}%", (bar_x + bar_len + 10, h - 26), FONT, 0.65, WHITE, 2)
    else:
        hint = "Show your hand to begin"
        (tw, _), _ = cv2.getTextSize(hint, FONT, 0.9, 2)
        cv2.putText(frame, hint, ((w - tw) // 2, h - 60), FONT, 0.9, MID_GREY, 2)
    cv2.putText(frame, "1 ASL  2 Gesture  SPACE freeze  R reset  Q quit",
                (w - 440, h - 10), FONT, 0.4, MID_GREY, 1)
    return frame
