import services.CallSql as CallSql
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
import pyodbc
import threading
import cv2
from ultralytics import YOLO
import uuid
import function.lineAlert as lineAlert
import datetime
import time

app=Flask(__name__,static_folder='static')

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('QXOpsah7x1u7z32mpTd0Hnhv+XcbDxO3ua4HHrdxj9IWZA0Ow74ZdMa50AjeplzID6YMHxVUjVGQP/XzXEqbhCk4lL0QTzbAoSRRD/qGqKINvexHgeTgMSGGv7vI5/gzorNX761VhCjIZu3xjf8NgAdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('51aeadc5c1eb9f92d3c777e2a6be34f9')
#line_bot_api.push_message('U83b2468825f9b4c101039e594a9a8446', TextSendMessage(text='你可以開始了'))


#取得所有使用者的ID
def lineUserFetch(): 
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=MSI;'
                          'Database=HomeSafty;'
                          'UID=sa;'
                          'PWD=123456;')
    cursor = conn.cursor()
    sql = "SELECT userId FROM LineUserId "
    cursor.execute(sql)
    userIds = cursor.fetchall()
    cursor.commit()
    # 關閉連接
    conn.close()
    return userIds
def IdSaveInSql(userId):
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=MSI;'
                          'Database=HomeSafty;'
                          'UID=sa;'
                          'PWD=123456;')
    cursor = conn.cursor()
    data=(userId)
    sql = "INSERT INTO LineUserId  (userId) VALUES ( ? )"
    cursor.execute(sql,data)
    cursor.commit()
    # 關閉連接
    conn.close()
    print("儲存成功")
    
#line user確認是否有登入
def lineUserComfirm(userId): 
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=MSI;'
                          'Database=HomeSafty;'
                          'UID=sa;'
                          'PWD=123456;')
    cursor = conn.cursor()
    sql = "SELECT * FROM LineUserId WHERE userId = ?"
    cursor.execute(sql,userId)
    records = cursor.fetchall()
    cursor.commit()
    # 關閉連接
    conn.close()
    if len(records) == 0:
        print('未登入之ID，執行登入')
        IdSaveInSql(userId)

#domain 初始化
#ngrok=input("輸入你的domainName:")
ngrok=""
#對所有人傳訊息
for i in lineUserFetch():
    print(i.userId)
    line_bot_api.push_message(i.userId, TextSendMessage(text='系統開啟'))

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
    lineUserComfirm(UserId)
    if re.match('目前畫面',message):
        line_bot_api.reply_message(event.reply_token,TextSendMessage('鏡頭畫面開啟:'+ngrok+'cam'))#+ngrok+'cam'
        print("剛剛傳了訊息")
    if re.match('歷史紀錄',message):
        line_bot_api.reply_message(event.reply_token,TextSendMessage('歷史紀錄頁面:'+ngrok))#+ngrok
        print("剛剛傳了訊息")


#紀錄首頁
@app.route("/")
def getRecords():
    records=CallSql.SelectALL()
    return render_template("records.html",records=records)

#記錄 查看 編輯
@app.route('/detail/<id>' ,methods=['GET','POST'])
def detail(id):
    if request.method == 'GET':
        detail=CallSql.SelectOne(id)
        return render_template("detail.html",detail=detail)
    if request.method == 'POST':
        name = request.form.get('name')
        opration = request.form.get('opration')
        type=request.form.get('type')
        CallSql.DataUpdate(name,opration,id,type)
        return redirect(url_for('detail', id=id))

#刪除紀錄
@app.route('/detailDelete/<id>/<path:Imgpath>' ,methods=['POST'])
def detailDelete(id,Imgpath):
    try:
        os.remove("./static/photo/saveData/"+Imgpath)
        print("照片已成功刪除")
    except OSError as e:
        print(f"刪除照片時出現錯誤: {e}")
    if CallSql.DataDelete(id):
        return getRecords()

#鏡頭畫面
import function.detectAndDraw as dd
import numpy as np   
counter=0
face_match1=False
face_match2=False

def generate_frames():
    global counter
    camera1 = cv2.VideoCapture(0)  # 第一個相機
    camera2 = cv2.VideoCapture(1)  # 第二個相機
    
    while True:
        success1, frame1 = camera1.read()
        success2, frame2 = camera2.read()
        

        
        # 調整兩個相機的大小相等
        frame1 = cv2.resize(frame1, (640, 480))  # 調整大小為 640x480
        frame2 = cv2.resize(frame2, (640, 480))  # 調整大小為 640x480

        

        # 在兩個相機畫面中間建立白色縫隙
        white_separator = np.full((480, 10, 3), 255, dtype=np.uint8)
            
        # 合併兩個相機的影像
        combined_frame = np.hstack((frame1, white_separator, frame2))
            
        ret, buffer = cv2.imencode('.jpg', combined_frame)
        frame = buffer.tobytes()  
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    camera1.release()
    camera2.release()

# 影像網頁的路由
@app.route('/cam')
def cam():
    return render_template('camStream.html')

# 影像串流的路由
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)