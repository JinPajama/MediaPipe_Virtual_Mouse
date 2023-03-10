import cv2
import time
import mediapipe
import math, numpy as np
import autopy ,pyautogui
import sys
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

cap = cv2.VideoCapture(0)                           #비디오 캡쳐
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)              
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 60)

initHand = mediapipe.solutions.hands  # Initializing mediapipe
# Object of mediapipe with "arguments for the hands module" 미디어파이프 내부 핸즈 모듈 
mainHand = initHand.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8) # 80% 이상의 정확도일 경우에만 탐지 및 추적
draw = mediapipe.solutions.drawing_utils  # 각 핑거 인덱스 간의 연결을 그릴 개체 (랜드마크 사이 선)
wScr, hScr = autopy.screen.size()  # 화면의 높이와 너비를 출력 (1920 x 1080)
scale_factor_x = wScr / 640
scale_factor_y = hScr / 480
pX, pY = 0, 0  # Previous x and y location  # 마우스 지터링 방지를 위한 이전 x,y 좌표값 변수
cX, cY = 0, 0  # Current x and y location   # 현재 마우스 좌표 변수

devices = AudioUtilities.GetSpeakers()  # pycaw 내부 함수, 볼륨조절 용도
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()

minVol = volRange[0]                          # -65.25       pycaw 내부 0 = -65.25 맵핑
maxVol = volRange[1]                          #   0.0
print(volRange)
hmin = 10                                     # 화면 좌표상 minimum 볼륨 거리
hmax = 150                                    # 화면 좌표상 max 볼륨 거리

pyautogui.FAILSAFE = False                    # 종료 안전장치 (좌표값 0.0 도달 시 종료, 추후 수정 가능)

def handLandmarks(colorImg):                  # 이미지 한 장을 받아 손에 있는 21가지 관절 번호 부여
    landmarkList = []  # Default values if no landmarks are tracked  아무런 랜드마크 트래킹 안될 경우 빈 배열 값
    global wh          # 왼손 오른손 구별을 위한 전역변수

    landmarkPositions = mainHand.process(colorImg)          # Object for processing the video input
    landmarkCheck = landmarkPositions.multi_hand_landmarks  # Stores the out of the processing object (returns False on empty)
    if landmarkCheck:  # Checks if landmarks are tracked
        for hand in landmarkCheck:  # Landmarks for each hand
            for index, landmark in enumerate(hand.landmark):  # Loops through the 21 indexes and outputs their landmark coordinates (x, y, & z)
                which_hand = landmarkPositions.multi_handedness[0].classification[0].label
                wh = which_hand
                if wh == "Right":
                    draw.draw_landmarks(img, hand, initHand.HAND_CONNECTIONS)  # Draws each individual index on the hand with connections
                    h, w, c = img.shape  # Height, width and channel on the image
                    centerX, centerY = int(landmark.x * w), int(landmark.y * h)  # Converts the decimal coordinates relative to the image for each index
                    landmarkList.append([index, centerX, centerY])  # Adding index and its coordinates to a list

                elif wh == "Left":
                    draw.draw_landmarks(img, hand, initHand.HAND_CONNECTIONS)  # Draws each individual index on the hand with connections
                    h, w, c = img.shape  # Height, width and channel on the image
                    centerX, centerY = int(landmark.x * w), int(landmark.y * h)  # Converts the decimal coordinates relative to the image for each index
                    landmarkList.append([index, centerX, centerY])  # Adding index and its coordinates to a list
                
    return landmarkList


def fingers(landmarks):                     # 손가락 접힘을 0과 1로 구분하는 함수 fingers
    fingerTips = []  # To store 4 sets of 1s or 0s
    tipIds = [4, 8, 12, 16, 20]  # Indexes for the tips of each finger
    
    if wh == "Right":
    # Check if thumb is up
        if landmarks[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
            fingerTips.append(1)
        else:
            fingerTips.append(0)
    if wh == "Left":
        if landmarks[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            fingerTips.append(1)
        else:
            fingerTips.append(0)
        
    
    # Check if fingers are up except the thumb
    for id in range(1, 5): # 2번째 ~ 5번째 손가락
        if landmarks[tipIds[id]][2] < landmarks[tipIds[id] - 3][2]:  # Checks to see if the tip of the finger is higher than the joint
            fingerTips.append(1)
        else:
            fingerTips.append(0)
            
    return fingerTips

i = 0 # 새끼손가락 인식으로 프로그램 종료 시, 딜레이를 위한 변수
j = 0
class Controll:
    flag = False
    grabflag = False
    
while True:                 # 영상 처리 시작
    check, img = cap.read()  # Reads frames from the camera
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # BGR to RGB 변환
    lmList = handLandmarks(imgRGB)
    # cv2.rectangle(img, (75, 75), (640 - 75, 480 - 75), (255, 0, 255), 2)

    if len(lmList) != 0:    # 이미지가 존재한다면
        x1, y1 = lmList[8][1:]  # 검지 좌표
        x2, y2 = lmList[4][1:]  # 엄지 좌표
        x4, y4 = lmList[9][1:]
        finger = fingers(lmList)  # finger에 손가락 접힘 0, 1 구분 배열 전달
        
        if finger == [1,1,1,1,1]:  # 포인팅 핑거가 위에 있고 엄지손가락이 아래에 있는지 확인
            x3 = np.interp(x4, (75, 640 - 75), (0, wScr))  # 화면 너비를 기준으로 보간법
            y3 = np.interp(y4, (75, 480 - 75), (0, hScr))  # 화면 높이를 기준으로 보간법
            
            cX = pX + (x3 - pX)/3  # 지터링 방지 및 부드러운 움직임을 위한 보간법 값 나누기
            cY = pY + (y3 - pY)/3 
            
            Controll.flag = True
            autopy.mouse.move(wScr-cX, cY)  # x축 값은 카메라 기준 좌우반전, y축은 반전 필요 x
            pX, pY = cX, cY  # pre 값에 current 값 넣어주기
            
        if finger == [0,1,1,1,1] and Controll.flag:  # Checks to see if the pointer finger is down and thumb finger is up
            pyautogui.click()  # Left click
            Controll.flag = False
        
        if finger == [1,0,1,1,1] and Controll.flag:  # Checks to see if the pointer finger is down and thumb finger is up
            pyautogui.click(button= 'right')  # Left click
            Controll.flag = False
        
        if finger == [0,0,0,0,0]:
            if not Controll.grabflag:
                Controll.grabflag = True
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)

            x3 = np.interp(x4, (75, 640 - 75), (0, wScr))  # 화면 너비를 기준으로 보간법
            y3 = np.interp(y4, (75, 480 - 75), (0, hScr))  # 화면 높이를 기준으로 보간법
            
            cX = pX + (x3 - pX)/3  # 지터링 방지 및 부드러운 움직임을 위한 보간법 값 나누기
            cY = pY + (y3 - pY)/3

            autopy.mouse.move(wScr-cX, cY)  # x축 값은 카메라 기준 좌우반전, y축은 반전 필요 x
            pX, pY = cX, cY  # pre 값에 current 값 넣어주기
            
        if finger != [0,0,0,0,0]:
            Controll.grabflag = False
            autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
                            
        
        if finger == [0,1,0,0,0]:
            pyautogui.scroll(100)
        
        if finger == [0,1,1,0,0]:
            pyautogui.scroll(-100)
        
        if finger == [1,1,0,0,0]:
            length = math.hypot(x1 - x2, y1 - y2)
            vol = np.interp(length, [hmin, hmax], [minVol, maxVol])
            volN = int(vol)
            if volN % 4 != 0:
                volN = volN - volN % 4
                if volN >= 0:
                    volN = 0
                elif volN <= -64:
                    volN = -64
                elif volN >= -11:
                    volN = vol
            volume.SetMasterVolumeLevel(vol, None) 
        
        # Exit gesture 1sec maintain
        if finger == [0,0,0,0,1]:
            i += 1
            time.sleep(0.05)
            
        if i > 15 :
            sys.exit(0) 


    img = cv2.flip(img, 1)            #인간이 보기 편한 거울 화면으로 출력
    cv2.imshow("Webcam", img)         #웹캠 출력
    if cv2.waitKey(1) & 0xFF == 27:   #Esc 누르면 종료
        break