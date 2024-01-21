import os,cv2
from deepface import DeepFace
import ray


@ray.remote
def face_recognition(img):
    result = DeepFace.find(img_path=img, db_path=r"function\faceData", model_name="Facenet512")#enforce_detection=False
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

@ray.remote
def faceResultDraw(data,img):
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
                org = (x+10 , y+30 )
                name=os.path.splitext(name)[0]#去掉檔名
                name=name.split("/")
                ouputname.append(name[-1])
                img=cv2.putText(img, name[-1], org, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    return img,ouputname