import mediapipe as mp
import cv2
import numpy as np
import time
import sys
import math
import os

ml = 150
max_x, max_y = 250 + ml, 50
curr_tool = "select tool"
time_init = True
rad = 40
var_inits = False
thick = 4
thick_min = 1
thick_max = 10
prevx, prevy = 0, 0
thickness = ""
width = 640
height = 480
i = 0
code = (0,255,0)

hmin = 13
hmax = 128

def getTool(x):
    if x < 50 + ml:
        return "line"
    elif x < 100 + ml:
        return "rectangle"
    elif x < 150 + ml:
        return "draw"
    elif x < 200 + ml:
        return "circle"
    else:
        return "erase"
    
def index_raised(yi, y9):
    if (y9 - yi) > 40:
        return True
    
    return False

cap =cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

initHand = mp.solutions.hands
mainHand = initHand.Hands(min_detection_confidence = 0.6, min_tracking_confidence = 0.6, max_num_hands = 1)
draw = mp.solutions.drawing_utils

tools = cv2.imread("photo/tools.png")
tools = tools.astype('uint8')

imgCanvas = np.zeros((height, width, 3), np.uint8)
imgCanvas.fill(255)

mask = np.ones((height,width))*255
mask = mask.astype('uint8')

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
                   # draw.draw_landmarks(frm, hand, initHand.HAND_CONNECTIONS)  # Draws each individual index on the hand with connections
                    h, w, c = frm.shape  # Height, width and channel on the image
                    centerX, centerY = int(landmark.x * w), int(landmark.y * h)  # Converts the decimal coordinates relative to the image for each index
                    landmarkList.append([index, centerX, centerY])  # Adding index and its coordinates to a list

                elif wh == "Left":
                   # draw.draw_landmarks(frm, hand, initHand.HAND_CONNECTIONS)  # Draws each individual index on the hand with connections
                    h, w, c = frm.shape  # Height, width and channel on the image
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

j = 0
k = 0
z = 2
while True:
    if os.path.exists("stop.txt"):
        break
    
    _, frm = cap.read()
    frm = cv2.flip(frm, 1)

    rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)

    op = mainHand.process(rgb)
    lmList = handLandmarks(rgb)

    if len(lmList) != 0:    # 이미지가 존재한다면
        x1, y1 = lmList[8][1:]  # 검지 좌표
        x2, y2 = lmList[4][1:]  # 엄지 좌표
        x4, y4 = lmList[9][1:]
        finger = fingers(lmList)  # finger에 손가락 접힘 0, 1 구분 배열 전달

        if finger == [1,1,0,0,0]:
            length = math.hypot(x1 - x2, y1 - y2)
            length1 = int(length)
            thick = int(np.interp(length1, [hmin, hmax], [thick_min, thick_max]))
            print(thick)
            thickness = "{}".format(thick)
        
        if finger == [1,0,0,0,1]:
            z = 0
            k = 1
            code = (0,0,255)
        
        if finger == [0,1,0,0,1]:
            z = 1
            k = 2
            code = (255,0,0)

        if finger == [0,0,0,1,1]:
            z = 2
            k = 0
            code = (0,255,0)
        
        if finger == [0,0,0,0,1]:
            j += 1
            time.sleep(0.05)
            
        if j > 15 :
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)
            
    if op.multi_hand_landmarks:
        for i in op.multi_hand_landmarks:
            draw.draw_landmarks(frm, i ,initHand.HAND_CONNECTIONS)
            x, y = int(i.landmark[8].x * width), int(i.landmark[8].y * height)

            if x < max_x and y < max_y and x > ml:      #선택
                if time_init:
                    ctime = time.time()
                    time_init = False
                ptime = time.time()

                cv2.circle(frm, (x, y), rad, (0, 255, 255), 2)
                rad -= 1

                if(ptime - ctime) > 0.8:
                    curr_tool = getTool(x)
                    print("your current tool set to : ", curr_tool)
                    time_init = True
                    rad = 40

            else: 
                time_init = True
                rad = 40
            
            if curr_tool == "draw":            # 그리기
                xi, yi = int(i.landmark[12].x * width), int(i.landmark[12].y * height)
                y9 = int(i.landmark[9].y * height)

                if index_raised(yi, y9):
                    cv2.line(mask, (prevx, prevy), (x, y), 0 , thick)
                    cv2.line(imgCanvas, (prevx, prevy), (x, y), code, thick)
                    prevx, prevy = x, y

                else: 
                    prevx = x
                    prevy = y

            elif curr_tool == "line":           #직선
                xi, yi = int(i.landmark[12].x * width), int(i.landmark[12].y * height)
                y9 = int(i.landmark[9].y * height)

                if index_raised(yi, y9):
                    if not(var_inits):
                        xii, yii = x,y
                        var_inits = True

                    cv2.line(frm, (xii, yii), (x, y), (50, 152, 255), thick)

                else:
                    if var_inits:
                        cv2.line(mask, (xii, yii), (x, y), 0 , thick)
                        cv2.line(imgCanvas, (xii, yii), (x, y), code, thick)
                        var_inits = False

            elif curr_tool == "rectangle":      #직사각형
                xi, yi = int(i.landmark[12].x * width), int(i.landmark[12].y * height)
                y9 = int(i.landmark[9].y * height)

                if index_raised(yi, y9):
                    if not(var_inits):
                        xii, yii = x,y
                        var_inits = True

                    cv2.rectangle(frm, (xii, yii), (x, y), (0, 255, 255), thick)

                else:
                    if var_inits:
                        cv2.rectangle(mask, (xii, yii), (x, y), 0 , thick)
                        cv2.rectangle(imgCanvas, (xii, yii), (x, y), code, thick)
                        var_inits = False

            elif curr_tool == "circle":         # 원
                xi, yi = int(i.landmark[12].x * width), int(i.landmark[12].y * height)
                y9 = int(i.landmark[9].y * height)

                if index_raised(yi, y9):
                    if not(var_inits):
                        xii, yii = x,y
                        var_inits = True

                    cv2.circle(frm, (xii, yii), int(((xii-x)**2 + (yii-y)**2)**0.5), (255, 255, 0), thick)

                else:
                    if var_inits:
                        cv2.circle(mask, (xii, yii), int(((xii-x)**2 + (yii-y)**2)**0.5), 0 , thick)
                        cv2.circle(imgCanvas, (xii, yii), int(((xii-x)**2 + (yii-y)**2)**0.5), code, thick)
                        var_inits = False

            elif curr_tool == "erase":          # 지우개 
                xi, yi = int(i.landmark[12].x * width), int(i.landmark[12].y * height)
                y9 = int(i.landmark[9].y * height)

                if index_raised(yi, y9):
                    cv2.circle(frm, (x, y), 30, (0,0,0), -1)
                    cv2.circle(mask, (x, y), 30, 255, -1)
                    cv2.circle(imgCanvas, (x, y), 30, (255,255,255), -1)

    op = cv2.bitwise_and(frm, frm, mask=mask)

    frm[:,:,z] = op[:,:,z]
    frm[:,:,k] = op[:,:,k]

    frm[:max_y,ml:max_x] = cv2.addWeighted(tools, 0.7, frm[:max_y, ml:max_x], 0.3, 0)

    cv2.putText(frm, curr_tool,(270 + ml, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    cv2.putText(frm, thickness,(450 + ml, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("AIVB", frm)
    cv2.imshow("Canvas", imgCanvas)

    if cv2.waitKey(1) == 27:
        cv2.destroyAllWindows()
        cap.release()
        break