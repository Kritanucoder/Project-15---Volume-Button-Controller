import cv2
import mediapipe as mp
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

mp_draw= mp.solutions.drawing_utils
mp_draw_style = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol, maxVol, volBar, volPer = volRange[0], volRange[1], 400, 0

wcam, hcam = 640, 480
cam=cv2.VideoCapture(0)
cam.set(3,wcam)
cam.set(4,hcam)

with mp_hands.Hands(
    model_complexity = 0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands:
    while cam.isOpened():
        success, img = cam.read()
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(
                    img, 
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_draw_style.get_default_hand_landmarks_style(),
                    mp_draw_style.get_default_hand_connections_style()
                )
        lmList = []
        if results.multi_hand_landmarks:
            myHand = results.multi_hand_landmarks[0]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                lmList.append([id, cx, cy])
        
        if len(lmList)!=0:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            
            cv2.circle(img, (x1, y1), 15, (255, 255, 255))
            cv2.circle(img, (x2, y2), 15, (255, 255, 255))
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            length = math.hypot(x2-x1, y2-y1)
            if length < 50:
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
                
            vol = np.interp(length, [50, 220], [minVol, maxVol])
            volume.SetMasterVolumeLevel(vol, None)
            volBar = np.interp(length, [50, 220], [400, 150])
            volPer = np.interp(length, [50, 220], [0,100])
            
            cv2.rectangle(img, (50, 150), (85, 400), (0,0,0), 3)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 0, 0), cv2.FILLED)
            cv2.putText(img, f'{int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                        1, (0,0,0), 3)
        cv2.imshow('handDetector', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
cam.release()
            
            