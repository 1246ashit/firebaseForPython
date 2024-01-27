from flask import (Blueprint,
                   render_template,Response
                   )
import Controller.Setting as Setting
import Services.FaceRecognition3 as FR
import Services.YoloDerect as YD
import Services.Alert as Alert
from ultralytics import YOLO
import ray
import cv2
from datetime import datetime, timedelta
ray.init()

CamBP = Blueprint('Cam', __name__)
yoloModel=YOLO(r'function\FireAndAction240102_1723\weights\best.pt')
counter=0
faceTemp=[False,False]
yoloTemp=[[],[]]
counter=[1,15]
initTime = datetime.now() + timedelta(seconds=10)
namedic=Setting.namedic


# 在這裡設定捕捉攝影機畫面的函式
def capture_camera(camera_id):
    global faceTemp,yoloTemp,counter,initTime,namedic
    camera = cv2.VideoCapture(camera_id)
    while True:
        success, frame = camera.read()
        frame = cv2.resize(frame,(640,480))
        if not success:
            break
        #deepface 每三十幀做一次
        if counter[camera_id]%10==0:
            counter[camera_id]=1
            faceTemp[camera_id]=ray.get(FR.face_recognition.remote(frame))
            yoloTemp[camera_id]=YD.detect(yoloModel,frame)
        else:
            counter[camera_id]+=1
        ###
        #畫出來
        frame,ouputname=ray.get(FR.faceResultDraw.remote(faceTemp[camera_id],frame,namedic))#臉部
        frame=YD.draw(yoloTemp[camera_id],frame)
        ###
        #警報
        reportType=[]
        classname=YD.ouputtype(yoloTemp[camera_id])
        if "火災" in classname:
            reportType.append("火災")
        if "跌倒" in classname:
            reportType.append("跌倒")
        
        print(reportType,ouputname)
        now=datetime.now()
        if now>initTime:
            if Alert.alert(reportType,ouputname,frame):
                initTime=now+timedelta(seconds=30)
                print("觸發警報")
        ###
        
        # 在這裡對 frame 做處理，比如轉換成 JPEG 格式
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        


# 影像網頁的路由
@CamBP.route('/cam')
def cam():
    return render_template('camStream.html')



# 影像串流的路由
# 使用 streaming 輸出攝影機畫面
@CamBP.route('/video_feed_1')
def video_feed_1():
    return Response(capture_camera(0), mimetype='multipart/x-mixed-replace; boundary=frame')

@CamBP.route('/video_feed_2')
def video_feed_2():
    return Response(capture_camera(1), mimetype='multipart/x-mixed-replace; boundary=frame')
