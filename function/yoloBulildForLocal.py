from ultralytics import YOLO
import cv2
import cvzone
import math
import function.facedetect3 as facedetect3

#臉部模型建立
facedetect3.encodeFaces("faces")
#火焰模型建立
fireModel = YOLO('function/fireModel/fire1/weight/fire_01.pt')
#姿勢模型建立
actionModel=YOLO('function/fallmodel/model/weight/best.pt')



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
#draw on image
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

def video_detection(frame):
    global fireModel 
    global actionModel
    needReport=0
    #臉部偵測區
    faceResult=facedetect3.runRecognition(frame)
    #yolo
    frame = cv2.resize(frame,(640,480))
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
    #如果有預測到火就秀   
    #畫出臉部
    frame=facedetect3.drawInImg(face_names=faceResult[0],img=frame,face_locations=faceResult[1])
    
    #faceResult[0] 印出名子
    #needReport 災害類型
    return frame,needReport,faceResult[0]