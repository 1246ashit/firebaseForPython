import os,cv2
from deepface import DeepFace
import ray
from PIL import Image, ImageDraw, ImageFont
import numpy as np

@ray.remote
def face_recognition(img):
    result = DeepFace.find(img_path=img, db_path=r"function\faceData", model_name="Facenet512",enforce_detection=False)#enforce_detection=False
    for i in result:
        try:
            name = i.at[0, "identity"]
            x = i.at[0, "source_x"]
            y = i.at[0, "source_y"]
            w = i.at[0, "source_w"]
            h = i.at[0, "source_h"]
            print(name, x, y, h,w)
            output=[]
            output.append({"name":name, "x":x, "y":y,"h": h,"w":w})
            return output
        except KeyError:
            print("沒東西")
            return False
        
def cv2_putText_chinese(img, text, position, font_size, color):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font_path = r"function\Noto_Sans_TC\NotoSansTC-VariableFont_wght.ttf"  # 指定字體檔案路徑
    font = ImageFont.truetype(font_path, font_size)
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)




@ray.remote
def faceResultDraw(data,img,namedic):
    ouputname=[]
    if data:
        if data[0]:
            for i in range(len(data)):
                mydict = data[i]
                name=mydict['name']
                x=mydict["x"]
                y=mydict["y"]
                w=mydict["w"]
                h=mydict["h"]
                start_point = (x, y)  # 矩形左上角的座標 (x, y)
                end_point = (x+w, y+h)    # 矩形右下角的座標 (x, y)
                # 在圖像上繪製矩形
                img = cv2.rectangle(img, start_point, end_point, (255, 0, 0), 2)
                #標籤
                end_point = (x+w, y+(h//4))    # 矩形右下角的座標 (x, y)
                img = cv2.rectangle(img, start_point, end_point, (255, 0, 0), -1)
                org = (x+5 , y+15 )

                
                name=name.split("/")
                ouputname.append(namedic[name[-1]])
                img = cv2_putText_chinese(img, f' {namedic[name[-1]]} ', org, 20, (255, 255, 255))
    return img,ouputname