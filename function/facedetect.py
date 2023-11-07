import cv2 
from deepface import DeepFace
import os
#臉部模型建立
#res_ = DeepFace.find(img_path = "function/faceData/jj.jpg", db_path = "function/faceData",model_name="Facenet512")#辨識

def facecompare(img):
    face_match=[]
    result = DeepFace.find(img_path = img, db_path = "function/faceData",model_name="Facenet512")#辨識和生產模組
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