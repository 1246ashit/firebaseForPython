from ultralytics import YOLO
import math
import cv2
import cvzone
from deepface import DeepFace
import os
#import function.detectAndDraw as detectAndDraw 


#臉部模型建立
def facecompare(img):
    face_match=[]
    result = DeepFace.find(img_path = img, db_path = "function/faceData",model_name="Facenet512",enforce_detection= False)#辨識
    for faceData in result: # 用迴圈取出有辨識到的人和位置
        try:
            name=faceData.at[0, "identity"]
            x=faceData.at[0, "source_x"]
            y=faceData.at[0, "source_y"]
            w=faceData.at[0, "source_w"]
            h=faceData.at[0, "source_h"]
            face_match.append([name,x,y,w,h])
        except KeyError:
            continue
    return face_match  
#yolo 
def ModelSet(frame,model,classnames):
    result = model(frame,stream=True)
    for info in result:
        boxes = info.boxes
        for box in boxes:
            confidence = box.conf[0]
            confidence = math.ceil(confidence * 100)
            classNum = int(box.cls[0])
            if confidence > 51:
                x1,y1,x2,y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1),int(y1),int(x2),int(y2)
                return x1, y1, x2, y2,classnames[classNum],confidence

#yolo 畫出來
def drawAndAlert(x1,y1,x2,y2,Class,confidence,img):
    needReport=0
    if Class=='fire':
        cv2.rectangle(img,(x1,y1),(x2,y2),(36, 36, 249),5)
        cvzone.putTextRect(img, f' {Class} {confidence}%', [x1+8, y1+20],
                                    scale=1.5,thickness=2)
        needReport="fire"
    if Class in ['sit','standing']:
        cv2.rectangle(img,(x1,y1),(x2,y2),(79, 249, 36),5)
        cvzone.putTextRect(img, f' {Class} {confidence}%', [x1+8, y1+80],
                                        scale=1.5,thickness=2)
    if Class == 'fallen':
        cv2.rectangle(img,(x1,y1),(x2,y2),(36, 36, 249),5)
        cvzone.putTextRect(img, f' {Class} {confidence}%', [x1+8, y1+80],
                                        scale=1.5,thickness=2)
        needReport="fallen"
    return img ,needReport

#deep face 畫出來
def faceResultDraw(img,name,x,y,w,h):
    start_point = (x, y)  # 矩形左上角的座標 (x, y)
    end_point = (x+w, y+h)    # 矩形右下角的座標 (x, y)
    # 在圖像上繪製矩形
    img = cv2.rectangle(img, start_point, end_point, (255, 0, 0), 2)
    #標籤
    end_point = (x+w, y+(h//4))    # 矩形右下角的座標 (x, y)
    img = cv2.rectangle(img, start_point, end_point, (255, 0, 0), -1)
    org = (x+10 , y+30 )
    name=os.path.splitext(name)[0]#去掉檔名
    name=name.split("/")
    img=cv2.putText(img, name[-1], org, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    return img


def detectandDraw(img,actionModel,fireModel):
    names=[]
    needReport=0
    #臉部偵測區
    face_match=facecompare(img)
    #yolo
    frame = cv2.resize(img,(640,480))
    #動作偵測區
    classNames = ['fallen','sit','standing']
    actionD=ModelSet(frame,actionModel,classNames)
    #火焰偵測區
    classnames = ['fire', 'smoke']
    fireD=ModelSet(frame,fireModel,classnames)


    #畫出來
    #如果有預測到動作就秀
    if actionD!=None:
        actionD=list(actionD)
        frame ,needReport=drawAndAlert(actionD[0],actionD[1],actionD[2],actionD[3],actionD[4],actionD[5],frame)
    #如果有預測到火就秀
    if fireD!=None:
        fireD=list(fireD)
        frame ,needReport=drawAndAlert(fireD[0],fireD[1],fireD[2],fireD[3],fireD[4],fireD[5],frame) 
    #劃出臉
    for i in face_match:
        name=os.path.splitext(i[0])[0]#取得名子
        name=name.split("/")[-1]
        names.append(name)
        frame=faceResultDraw(frame,name,i[1],i[2],i[3],i[4])
    
    return frame,needReport,names