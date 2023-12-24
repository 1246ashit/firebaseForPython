from ultralytics import YOLO
import math
import cv2
import cvzone

#yolo 
def YoloModelModelSet(frame,model,classnames):
    result = model(frame,stream=True)
    for info in result:
        boxes = info.boxes
        for box in boxes:
            confidence = box.conf[0]
            confidence = math.ceil(confidence * 100)
            classNum = int(box.cls[0])
            if confidence > 70:
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
    return img ,needReport


def YoloDetectAndDraw(frame,model,classNames):
    needReport=False
    #frame = cv2.resize(img,(640,480))
    #偵測區
    results = YoloModelModelSet(frame,
                                model,
                                classNames)
    #畫出來
    #
    if results!=None:
        results=list(results)
        frame ,needReport=drawAndAlert(results[0],results[1],results[2],results[3],results[4],results[5],frame) 
    
    return frame,needReport