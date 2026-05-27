import cv2
import mediapipe as mp
import numpy as np
import pickle
import os
from collections import deque, Counter
BASE_DIR  = r"C:\SignEase\SignEase"
MODEL_DIR = os.path.join(BASE_DIR, "models")
single_model_path = os.path.join(MODEL_DIR, "isl_single.pkl")
double_model_path = os.path.join(MODEL_DIR, "isl_double.pkl")
if not os.path.exists(single_model_path):
    raise Exception("isl_single.pkl not found — run train_model.py first")
single_model = pickle.load(open(single_model_path, "rb"))
double_model = None
if os.path.exists(double_model_path):
    double_model = pickle.load(open(double_model_path, "rb"))
mp_hands = mp.solutions.hands
hands    = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    model_complexity=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
mp_draw = mp.solutions.drawing_utils
running = False
cap     = None
prediction_buffer    = deque(maxlen=15)
CONFIDENCE_THRESHOLD = 0.55
WHOLE_WORD_SIGNS = {
    "Hello", "Please", "Sad", "Student", "Teacher",
    "Book", "Brother", "Father", "Mother", "Thank-You",
    "Anger", "Happy", "Thank You"
}
def normalize_word_label(word):
    return word.replace(" ", "-")
session_stats = {
    "correct": 0,
    "wrong": 0,
    "history": []
}
def reset_session_stats():
    session_stats["correct"] = 0
    session_stats["wrong"]   = 0
    session_stats["history"].clear()
def normalize_landmarks(hand_landmarks):
    coords = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
    coords -= coords[0]
    scale = np.linalg.norm(coords[9])
    if scale > 0:
        coords /= scale
    fingertips = [4, 8, 12, 16, 20]
    distances  = []
    for i in range(len(fingertips)):
        for j in range(i + 1, len(fingertips)):
            distances.append(np.linalg.norm(coords[fingertips[i]] - coords[fingertips[j]]))
    return list(coords.flatten()) + distances
def normalize_two_hands(multi_hand_landmarks, multi_handedness):
    right = left = None
    for lm, hd in zip(multi_hand_landmarks, multi_handedness):
        label = hd.classification[0].label
        if label == "Right": right = lm
        else:                left  = lm
    if right is None or left is None:
        right = multi_hand_landmarks[0]
        left  = multi_hand_landmarks[1]
    return list(normalize_landmarks(right)) + list(normalize_landmarks(left))
def get_stable_prediction(label):
    prediction_buffer.append(label)
    counts = Counter(prediction_buffer)
    top_label, top_count = counts.most_common(1)[0]
    if top_count / len(prediction_buffer) >= 0.5:
        return top_label
    return "..."
def predict_with_confidence(model, features):
    try:
        proba = model.predict_proba([features])[0]
        idx   = np.argmax(proba)
        return model.classes_[idx], proba[idx]
    except Exception:
        return model.predict([features])[0], 1.0
def get_prediction(result):
    num_hands = len(result.multi_hand_landmarks) if result.multi_hand_landmarks else 0
    label, confidence, model_tag = "No Hand", 0.0, "-"
    if num_hands == 2 and double_model is not None:
        features = normalize_two_hands(result.multi_hand_landmarks, result.multi_handedness)
        if features:
            raw_label, confidence = predict_with_confidence(double_model, features)
            label     = get_stable_prediction(raw_label) if confidence >= CONFIDENCE_THRESHOLD else "Low confidence"
            model_tag = "2-hand"
    elif num_hands >= 1:
        features  = normalize_landmarks(result.multi_hand_landmarks[0])
        raw_label, confidence = predict_with_confidence(single_model, features)
        label     = get_stable_prediction(raw_label) if confidence >= CONFIDENCE_THRESHOLD else "Low confidence"
        model_tag = "1-hand"
    return label, confidence, model_tag, num_hands
def run_webcam_detection():
    global running, cap
    running = True
    prediction_buffer.clear()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)
    if not cap.isOpened():
        print("Camera not opened")
        return
    WINDOW_NAME = "ISL Detection"
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 800, 500)
    while running:
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break
        ret, frame = cap.read()
        if not ret:
            break
        frame  = cv2.flip(frame, 1)
        result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        label, confidence, model_tag, _ = get_prediction(result)
        if result.multi_hand_landmarks:
            for hand_lm in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_lm, mp_hands.HAND_CONNECTIONS)
        cv2.rectangle(frame, (20, 10), (420, 110), (0,0,0), -1)
        cv2.rectangle(frame, (20, 10), (420, 110), (50,50,50), 1)
        cv2.putText(frame, f"Sign: {label}", (30, 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0,255,0), 2)
        conf_color = (0,255,0) if confidence >= 0.75 else (0,200,255) if confidence >= CONFIDENCE_THRESHOLD else (0,0,255)
        cv2.putText(frame, f"Confidence: {round(confidence*100,1)}%  [{model_tag}]",
                    (30, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, conf_color, 1)
        bar_w = 350
        cv2.rectangle(frame, (30, 95), (30+bar_w, 103), (60,60,60), -1)
        cv2.rectangle(frame, (30, 95), (30+int(bar_w*min(confidence,1.0)), 103), conf_color, -1)
        cv2.putText(frame, "Press Q to quit", (30, 490),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 1)
        cv2.imshow(WINDOW_NAME, frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    stop_webcam()
def practice_whole_word(target_word, on_result=None):
    global running, cap
    running = True
    prediction_buffer.clear()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)
    if not cap.isOpened():
        return
    WINDOW_NAME = "Practice Mode"
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 800, 500)
    expected_label = normalize_word_label(target_word)
    while running:
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break
        ret, frame = cap.read()
        if not ret:
            break
        frame  = cv2.flip(frame, 1)
        result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        label, confidence, model_tag, _ = get_prediction(result)
        if result.multi_hand_landmarks:
            for hand_lm in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_lm, mp_hands.HAND_CONNECTIONS)
        is_correct = (label == expected_label)
        if label in ("No Hand", "..."):
            feedback = "Show the sign!"
            fb_color = (180, 180, 0)
        elif is_correct:
            feedback = "Correct!  Press SPACE to confirm"
            fb_color = (0, 255, 0)
        else:
            feedback = f"Try again — detected: {label}"
            fb_color = (0, 80, 255)
        cv2.rectangle(frame, (20, 10), (760, 210), (0,0,0), -1)
        cv2.putText(frame, f"Sign the word:  {target_word}", (30, 52),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255,255,255), 2)
        cv2.putText(frame, f"Detected: {label}  ({round(confidence*100)}%)",
                    (30, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0,255,0), 2)
        cv2.putText(frame, feedback, (30, 165),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, fb_color, 2)
        cv2.putText(frame, "SPACE = submit    Q = quit",
                    (30, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 1)
        cv2.imshow(WINDOW_NAME, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord(" "):
            res = "correct" if is_correct else "wrong"
            session_stats["correct" if is_correct else "wrong"] += 1
            session_stats["history"].append({"word": target_word, "result": res})
            if on_result:
                on_result(target_word, res)
            break
    stop_webcam()
def practice_word(target_word, on_result=None):
    if target_word in WHOLE_WORD_SIGNS:
        practice_whole_word(target_word, on_result)
        return
    global running, cap
    running = True
    prediction_buffer.clear()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)
    if not cap.isOpened():
        return
    WINDOW_NAME = "Practice Mode"
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 800, 500)
    word_upper     = target_word.upper()
    letter_index   = 0
    total_letters  = len(word_upper)
    letter_results = []
    while running and letter_index < total_letters:
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break
        ret, frame = cap.read()
        if not ret:
            break
        frame  = cv2.flip(frame, 1)
        result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        label, confidence, _, _ = get_prediction(result)
        if result.multi_hand_landmarks:
            for hand_lm in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_lm, mp_hands.HAND_CONNECTIONS)
        expected   = word_upper[letter_index]
        is_correct = (label == expected)
        feedback   = "Correct!" if is_correct else ("Show your hand" if label in ("No Hand","...") else "Wrong")
        fb_color   = (0,255,0) if is_correct else (0,80,255)
        progress_str = ""
        for i, ch in enumerate(word_upper):
            if i < letter_index:
                progress_str += f"[{ch}] " if letter_results[i] == "correct" else f" {ch}  "
            elif i == letter_index:
                progress_str += f">{ch}< "
            else:
                progress_str += f" {ch}  "
        cv2.rectangle(frame, (20, 10), (760, 220), (0,0,0), -1)
        cv2.putText(frame, f"Word: {target_word}", (30, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255,255,255), 2)
        cv2.putText(frame, f"Sign letter: {expected}  ({letter_index+1}/{total_letters})",
                    (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (200,200,200), 2)
        cv2.putText(frame, f"Detected: {label}  ({round(confidence*100)}%)",
                    (30, 118), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
        cv2.putText(frame, feedback, (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.1, fb_color, 3)
        cv2.putText(frame, progress_str, (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220,220,100), 2)
        cv2.putText(frame, "SPACE = submit letter    Q = quit",
                    (30, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 1)
        cv2.imshow(WINDOW_NAME, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord(" "):
            res = "correct" if is_correct else "wrong"
            letter_results.append(res)
            session_stats["correct" if is_correct else "wrong"] += 1
            prediction_buffer.clear()
            letter_index += 1
    if letter_results:
        word_result = "correct" if all(r == "correct" for r in letter_results) else "wrong"
        session_stats["history"].append({"word": target_word, "result": word_result})
        if on_result:
            on_result(target_word, word_result)
    stop_webcam()
def stop_webcam():
    global running, cap
    running = False
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()