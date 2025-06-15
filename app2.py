import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
import pyautogui
import time

# Kamera başlatılır
cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)

# Göz kırpma kontrolü için değişkenler
idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
ratioList = []
blinkCounter = 0
counter = 0
doubleBlinkDetected = False
lastBlinkTime = 0
boxClicked = False
clickTime = 0

# Kutu konumu
boxWidth, boxHeight = 200, 150
boxX, boxY = 320, 240

while True:
    success, img = cap.read()
    if not success:
        print("Kamera görüntüsü alınamadı!")
        break

    img, faces = detector.findFaceMesh(img, draw=False)
    if faces:
        face = faces[0]

        leftUp = face[159]
        leftDown = face[23]
        leftLeft = face[130]
        leftRight = face[243]

        lengthVer, _ = detector.findDistance(leftUp, leftDown)
        lengthHor, _ = detector.findDistance(leftLeft, leftRight)

        ratio = int((lengthVer / lengthHor) * 100)
        ratioList.append(ratio)

        if len(ratioList) > 3:
            ratioList.pop(0)

        ratioAvg = sum(ratioList) / len(ratioList)

        if ratioAvg < 35 and counter == 0:
            currentTime = time.time()
            if currentTime - lastBlinkTime < 1:
                blinkCounter += 1
            else:
                blinkCounter = 1
            lastBlinkTime = currentTime
            counter = 1

        if counter != 0:
            counter += 1
            if counter > 10:
                counter = 0

        if blinkCounter >= 2 and not doubleBlinkDetected:
            doubleBlinkDetected = True
            blinkCounter = 0

            boxCenterX = boxX + boxWidth // 2
            boxCenterY = boxY + boxHeight // 2
            pyautogui.moveTo(boxCenterX, boxCenterY)
            pyautogui.click(boxCenterX, boxCenterY)

            boxClicked = True
            clickTime = time.time()

    if boxClicked and time.time() - clickTime < 1:
        boxColor = (0, 255, 0)
    else:
        boxColor = (255, 0, 0)
        boxClicked = False

    cv2.rectangle(img, (boxX, boxY), (boxX + boxWidth, boxY + boxHeight), boxColor, 2)
    cvzone.putTextRect(img, f'Blinks: {blinkCounter}', (50, 50))

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
