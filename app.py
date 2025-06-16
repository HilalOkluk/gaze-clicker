import cv2
import numpy as np
import pyautogui
import mediapipe as mp
import time
import keyboard

# MediaPipe FaceMesh başlat
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Göz landmark index'leri
LEFT_EYE = [159, 145]
RIGHT_EYE = [386, 374]
NOSE_INDEX = 1

# Tuşlar
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["Z", "X", "C", "V", "B", "N", "M"]]

keyboard_visible = False
typed_text = ""
previous_key = None
click_cooldown = 1
last_click_time = 0

screen_w, screen_h = pyautogui.size()

def draw_keys(frame, selected_key=None):
    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            x = j * 60 + 50
            y = i * 60 + 300
            color = (0, 255, 0) if key == selected_key else (200, 200, 200)
            cv2.rectangle(frame, (x, y), (x+50, y+50), color, -1)
            cv2.putText(frame, key, (x+15, y+35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

def get_key_under_nose(nose_x, nose_y):
    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            x = j * 60 + 50
            y = i * 60 + 300
            if x < nose_x < x+50 and y < nose_y < y+50:
                return key
    return None

def is_blinking(landmarks, eye_indices):
    y1 = landmarks[eye_indices[0]][1]
    y2 = landmarks[eye_indices[1]][1]
    return abs(y2 - y1) < 0.015

# Kamera başlat
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Kamera açılamadı.")
    exit()

cv2.namedWindow("GazeNoseClicker", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb_frame)

    if result.multi_face_landmarks:
        landmarks = result.multi_face_landmarks[0].landmark
        ih, iw, _ = frame.shape

        coords = [(int(l.x * iw), int(l.y * ih)) for l in landmarks]

        # Burun pozisyonu
        nose = coords[NOSE_INDEX]
        mouse_x = int((nose[0] / iw) * screen_w)
        mouse_y = int((nose[1] / ih) * screen_h)
        pyautogui.moveTo(mouse_x, mouse_y)

        # Göz kırpma kontrolü
        left_blink = is_blinking(landmarks, LEFT_EYE)
        right_blink = is_blinking(landmarks, RIGHT_EYE)

        if left_blink and not right_blink and time.time() - last_click_time > click_cooldown:
            pyautogui.click()
            last_click_time = time.time()

        elif right_blink and not left_blink and time.time() - last_click_time > click_cooldown:
            keyboard_visible = not keyboard_visible
            last_click_time = time.time()

        elif left_blink and right_blink and time.time() - last_click_time > click_cooldown:
            keyboard.press_and_release("ctrl+a")
            last_click_time = time.time()

        # Klavye işlemleri
        if keyboard_visible:
            draw_keys(frame)
            key_under_nose = get_key_under_nose(nose[0], nose[1])
            if key_under_nose and key_under_nose != previous_key:
                typed_text += key_under_nose
                previous_key = key_under_nose
        else:
            previous_key = None

    # Yazılan metin
    cv2.putText(frame, typed_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)

    cv2.imshow("GazeNoseClicker", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
