import cv2
from ultralytics import YOLO
import math
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def cv2_putText_chinese(img, text, position, font_size, color):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font_path = "function/Noto_Sans_TC/NotoSansTC-VariableFont_wght.ttf"  #中文字型模組
    font = ImageFont.truetype(font_path, font_size)
    # 繪製文字陰影
    shadow_color=(0, 0, 0)
    shadow_offset = 1  # 陰影偏移量
    draw.text((position[0] + shadow_offset, position[1] + shadow_offset), text, font=font, fill=shadow_color)
    # 繪製文字
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

#畫框框
def drawbox(img, x1, y1, x2, y2, classNames, conf):
    start_point = (x1, y1)  # 左上角坐標 (x, y)
    end_point = (x2, y2)  # 右下角坐標 (x, y)

    color = (0, 0, 255)  # 框框顏色 (BGR)
    thickness = 2  # 框框線條寬度

    text_color = (255, 255, 255)
    text_start_point = (x1, y1)  # 文字起始座標

    img = cv2.rectangle(img, start_point, (x2, y1 + 30), color, -1)  # 增大背景矩形以適應陰影

    img = cv2.rectangle(img, start_point, end_point, color, thickness)
    img = cv2_putText_chinese(img, f'{classNames} {conf}%', text_start_point, 20, text_color)

    return img

#解析資料跟畫
def draw(results,image):
    for info in results:
        boxes = info.boxes
        for box in boxes:
            #信心
            conf=math.ceil(box.conf[0] * 100)
            #類型
            classNames = ["跌倒","火災","坐","站立"]
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
        source=image,conf=0.7
    )
    return results

def ouputtype(results):
    name=[]
    for info in results:
        boxes = info.boxes
        for box in boxes:
            #類型
            classNames = ["跌倒","火災","坐","站立"]
            name.append(classNames[int(box.cls[0])])
    return name
