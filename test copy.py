from ultralytics import YOLO
import cv2
import os
import function.detectAndDraw as detectAndDraw 

#火焰模型建立
fireModel = YOLO('function/fireModel/fire1/weight/fire_01.pt')
#姿勢模型建立
actionModel=YOLO('function/fallmodel/model/weight/best.pt')

#攝像頭
cap=cv2.VideoCapture(0)
while True:
    ret,img=cap.read()

    #臉部偵測區
    face_match=detectAndDraw.facecompare(img)
    #yolo
    frame = cv2.resize(img,(640,480))
    #動作偵測區
    classNames = ['fallen','sit','standing']
    actionD=detectAndDraw.ModelSet(frame,actionModel,classNames)
    #火焰偵測區
    classnames = ['fire', 'smoke']
    fireD=detectAndDraw.ModelSet(frame,fireModel,classnames)

    #畫出來
    #如果有預測到動作就秀
    if actionD!=None:
        actionD=list(actionD)
        frame ,needReport=detectAndDraw.drawAndAlert(actionD[0],actionD[1],actionD[2],actionD[3],actionD[4],actionD[5],frame)
    #如果有預測到火就秀
    if fireD!=None:
        fireD=list(fireD)
        frame ,needReport=detectAndDraw.drawAndAlert(fireD[0],fireD[1],fireD[2],fireD[3],fireD[4],fireD[5],frame) 
    #劃出臉
    for i in face_match:
        name=os.path.splitext(i[0])[0]#取得名子
        name=name.split("/")
        frame=detectAndDraw.faceResultDraw(frame,name[-1],i[1],i[2],i[3],i[4])

    cv2.imshow("frame",frame)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()


