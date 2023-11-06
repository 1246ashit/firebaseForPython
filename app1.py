# %%
#載入LineBot所需要的套件
#from flask import Flask, request, abort
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
import function.detectAndDraw as detectAndDraw
import uuid
import function.lineAlert as lineAlert
import datetime
import time

# %%
app=Flask(__name__,static_folder='static')

# %%
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
ngrok=input("輸入你的domainName:")

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
    #else:
    #    line_bot_api.reply_message(event.reply_token, TextSendMessage(message))

# %%
#webpart
#紀錄首頁
@app.route("/")
def getRecords():
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=MSI;'
                          'Database=HomeSafty;'
                          'UID=sa;'
                          'PWD=123456;')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM records ORDER BY time DESC')
    records = cursor.fetchall()
    # 關閉連接
    conn.close()
    return render_template("records.html",records=records)

#記錄 查看 編輯
@app.route('/detail/<id>' ,methods=['GET','POST'])
def detail(id):
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=MSI;'
                          'Database=HomeSafty;'
                          'UID=sa;'
                          'PWD=123456;')
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute("select * from records where id= ?", id)
        detail = cursor.fetchone()
        # 關閉連接
        conn.close()
        return render_template("detail.html",detail=detail)
    if request.method=='DELETE':
        cursor.execute("DELETE FROM records WHERE id = ?", id)
        conn.commit()
        conn.close()
        return getRecords()
    else:
        name = request.form.get('name')
        opration = request.form.get('opration')
        sql = "UPDATE records SET "
        if name=='' and opration=='':
            return redirect(url_for('detail', id=id))
        if name!='':
            sql += "name = '%s' , " % name
        if opration!='':
            sql += "detail = '%s' , " % opration
        # 去除最後一個逗號和空格
        sql = sql[:-2]
        sql += " WHERE id = '%s'" % id
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return redirect(url_for('detail', id=id))

#刪除紀錄
@app.route('/detailDelete/<id>/<path:Imgpath>' ,methods=['POST'])
def detailDelete(id,Imgpath):
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=MSI;'
                          'Database=HomeSafty;'
                          'UID=sa;'
                          'PWD=123456;')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE id = ?", id)
    conn.commit()
    conn.close()

    try:
        os.remove("./static/photo/saveData/"+Imgpath)
        print("照片已成功刪除")
    except OSError as e:
        print(f"刪除照片時出現錯誤: {e}")
    return getRecords()


# %%

#鏡頭畫面
video_capture = cv2.VideoCapture(0)
frame = None
frame_lock = threading.Lock()#平行處理
should_capture_frame = False
#AI模組
#火焰模型建立
fireModel = YOLO('function/fireModel/fire1/weight/fire_01.pt')
#姿勢模型建立
actionModel=YOLO('function/fallmodel/model/weight/best.pt')
# 初始化冷卻時間
cooldown_time = 10  # 冷卻時間為40秒
# 警告是否已觸發的標誌
warning_triggered = False
#紀錄警告觸發的起始時間
start_time=0
#資料sql存入
def saveInSql(reportTime,names,photo_address,reportType):
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=MSI;'
                          'Database=HomeSafty;'
                          'UID=sa;'
                          'PWD=123456;')
    cursor = conn.cursor()
    nameStr=''
    for i in names:
        nameStr=''+i+','
    data=(reportTime,nameStr[:-1],photo_address,reportType)
    sql = "INSERT INTO records (time,name,photoLocation,type) VALUES ( ? ,? ,? ,?)"
    cursor.execute(sql,data)
    cursor.commit()
    # 關閉連接
    conn.close()
    print("儲存成功")
#通報
def alert(needReport,name,frame):
    global cooldown_time
    global warning_triggered 
    global start_time
    if needReport!=0:
        # 如果警告未觸發，則觸發警告並設定冷卻時間
        if not warning_triggered:
            print("Danger detected! Alert triggered.")
            # 儲存相片
            random_uuid = uuid.uuid4()
            photo_address=str(random_uuid)+'.jpg'
            cv2.imwrite("./static/photo/saveData/"+photo_address, frame)
            #line 警報
            imgURL=lineAlert.imgurUpload("./static/photo/saveData/"+photo_address)
            print('imgurl:',imgURL)
            #line 傳送API
            image_message = ImageSendMessage(
                    original_content_url=str(imgURL),
                    preview_image_url=str(imgURL)
                )
            for i in lineUserFetch():
                print(i.userId)
                line_bot_api.push_message(i.userId, image_message)
                line_bot_api.push_message(i.userId, TextSendMessage(text='有危險發生，類型:'+needReport))

            # 取得現在的日期
            current_time = datetime.datetime.now()
            #current_date = current_time.date() 
            saveInSql(current_time,name,photo_address,needReport)

            warning_triggered = True
            start_time = time.time()  # 紀錄警告觸發的起始時間
    else:
        # 如果警告已觸發且冷卻時間已過，則重置警告狀態
        if warning_triggered and time.time() - start_time > cooldown_time:
            warning_triggered = False
            print("Alert cooldown time passed.")

def capture_frames():
    global frame, should_capture_frame
    while True:
        if should_capture_frame:
            ret, frame = video_capture.read()
            #辨識
            #frame,needReport,name= yoloBulildForLocal.video_detection(frame)
            frame,needReport,names=detectAndDraw.detectandDraw(frame,actionModel,fireModel)
            #通報
            #alert(needReport,name,frame)
            alert(needReport,names,frame)
        else:
            frame = None

    
def generate_frames():
    global frame, should_capture_frame
    while True:
        with frame_lock:
            if frame is not None:
                ret, encoded_frame = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + encoded_frame.tobytes() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
#啟用攝像頭
@app.route('/start_capture')
def start_capture():
    global should_capture_frame
    should_capture_frame = True
    return ''
#停下攝像頭
@app.route('/stop_capture')
def stop_capture():
    global should_capture_frame
    should_capture_frame = False
    return ''

@app.route("/cam",methods=['GET'])
def cam():
    return render_template("camStream.html")

# %%
#主程式
import os
if __name__ == "__main__":
    thread = threading.Thread(target=capture_frames)
    thread.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


