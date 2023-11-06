from ultralytics import YOLO
import cv2

import function.detectAndDraw as detectAndDraw 

#火焰模型建立
fireModel = YOLO('function/fireModel/fire1/weight/fire_01.pt')
#姿勢模型建立
actionModel=YOLO('function/fallmodel/model/weight/best.pt')

#攝像頭
cap=cv2.VideoCapture(0)
while True:
    ret,img=cap.read()

    frame,needReport,names=detectAndDraw.detectandDraw(img,actionModel,fireModel)

    cv2.imshow("frame",frame)
    print(names,needReport)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()


