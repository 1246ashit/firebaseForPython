import cv2
from ultralytics import YOLO
import math
#畫框框
def drawbox(img,x1, y1, x2, y2,classNames,conf):
    start_point = (x1, y1)  # 左上角座標 (x, y)
    end_point = (x2, y2)  # 右下角座標 (x, y)

    # 定義框框的顏色和粗細
    color = (0, 0, 255)  # 框框顏色 (BGR)
    thickness = 2  # 框框線條寬度

    # 在框框附近繪製文字
    text_color = (255, 255, 255)  # 白色 (BGR)
    text_start_point = (x1, y1+20)  # 文字起始座標
    font = cv2.FONT_HERSHEY_SIMPLEX  # 字體
    font_scale = 0.8  # 字體縮放大小
    end_point2=(x2, y1+20)
    img = cv2.rectangle(img, start_point, end_point2, color, -1)
    
    # 在圖片上畫出框框
    image= cv2.rectangle(img, start_point, end_point, color, thickness)
    cv2.putText(img, f' {classNames} {conf}%', text_start_point, font, font_scale, text_color, 2)#標記
    return image

#解析資料跟畫
def draw(results,image):
    for info in results:
        boxes = info.boxes
        for box in boxes:
            #信心
            conf=math.ceil(box.conf[0] * 100)
            #類型
            classNames = ["fall","fire","sit","stand"]
            name=classNames[int(box.cls[0])]
            #位置
            x1,y1,x2,y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1),int(y1),int(x2),int(y2)
            #畫
            image=drawbox(image,x1, y1, x2, y2,name,conf)
    return image

#辨識
def detect(model,image):
    results =model.predict(
        source=image
    )
    return results

def ouputtype(results):
    name=[]
    for info in results:
        boxes = info.boxes
        for box in boxes:
            #類型
            classNames = ["fall","fire","sit","stand"]
            name.append(classNames[int(box.cls[0])])
    return name
