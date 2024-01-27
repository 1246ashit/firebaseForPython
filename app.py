import Services.CallSql as CallSql
import Controller.Setting as Setting
import Controller.Information as Information
from flask import(Flask,render_template,
                  Response,request,
                  flash,redirect,
                  url_for,session,
                  send_from_directory,abort
                ) 

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import re
import os
from pyngrok import ngrok
from Controller.Setting import settingsBP
from Controller.Information import InformationBP

app=Flask(__name__,static_folder='static')
app.config.from_object('config')

app.register_blueprint(settingsBP, url_prefix='/Settings')
app.register_blueprint(InformationBP)

# 必須放上自己的Channel Access Token
#line_bot_api = LineBotApi('QXOpsah7x1u7z32mpTd0Hnhv+XcbDxO3ua4HHrdxj9IWZA0Ow74ZdMa50AjeplzID6YMHxVUjVGQP/XzXEqbhCk4lL0QTzbAoSRRD/qGqKINvexHgeTgMSGGv7vI5/gzorNX761VhCjIZu3xjf8NgAdB04t89/1O/w1cDnyilFU=')
line_bot_api = LineBotApi(app.config['LINEPOT_API'])

# 必須放上自己的Channel Secret
handler = WebhookHandler(app.config['HANDLER'])

#line user確認是否有登入
def LineUserComfirm(userId): 
   if CallSql.LineUserComfirm(userId)!=True:
       if CallSql.registUser(userId):
           print(f"新User 加入:{userId}")

#domain 初始化
public_url = ngrok.connect(5000).public_url

#對所有人傳訊息
#for i in CallSql.fatchAllUser():
#    print(i.userId)
#    line_bot_api.push_message(i.userId, TextSendMessage(text='系統開啟'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    #取得用戶資訊
    UserId = event.source.user_id
    print(UserId)
    LineUserComfirm(UserId)
    if re.match('目前畫面',message):
        line_bot_api.reply_message(event.reply_token,TextSendMessage('鏡頭畫面開啟:'+public_url+'cam'))#+ngrok+'cam'
        print("剛剛傳了訊息")
    if re.match('歷史紀錄',message):
        line_bot_api.reply_message(event.reply_token,TextSendMessage('歷史紀錄頁面:'+public_url))#+ngrok
        print("剛剛傳了訊息")


#鏡頭畫面
import Services.FaceRecognition3 as FR
import Services.YoloDerect as YD
import Services.Alert as Alert
from ultralytics import YOLO
import ray
import cv2
from datetime import datetime, timedelta
ray.init()
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
        if "火災" in classname:
            reportType.append("火災")
        
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
@app.route('/cam')
def cam():
    return render_template('camStream.html')

# 影像串流的路由
# 使用 streaming 輸出攝影機畫面
@app.route('/video_feed_1')
def video_feed_1():
    return Response(capture_camera(0), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_2')
def video_feed_2():
    return Response(capture_camera(1), mimetype='multipart/x-mixed-replace; boundary=frame')


#主程式
import os
if __name__ == "__main__":
    # 啟動 ngrok 隧道
    print("ngrok 隧道 URL:",public_url)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)