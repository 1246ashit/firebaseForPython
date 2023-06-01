from flask import Flask,render_template,Response,request,flash,redirect,url_for,session
import os
import asyncio
import pyodbc
import threading
import function.yoloBulildForLocal as yoloBulildForLocal
import function.lineAlert as lineAlert
import cv2
import uuid
import datetime
import time

from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.models import ImageSendMessage

# 初始化冷卻時間
cooldown_time = 40  # 冷卻時間為40秒
# 警告是否已觸發的標誌
warning_triggered = False
#紀錄警告觸發的起始時間
start_time=0
#sql存入
def saveInSql(reportTime,names,photo_address,reportType):
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-009OG6J;'
                          'Database=homeSafty;'
                          'UID=sa;'
                          'PWD=123;')
    cursor = conn.cursor()
    nameStr=''
    for i in names:
        nameStr=''+i+','
    data=(reportTime,nameStr[:-1],photo_address,reportType)
    sql = "INSERT INTO records (time,name,photo_address,type) VALUES ( ? ,? ,? ,?)"
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
            photo_address="./static/photo/data_photo/"+str(random_uuid)+'.jpg'
            cv2.imwrite(photo_address, frame)
            #line 警報
            imgURL=lineAlert.uploadimg(photo_address)
            print('imgurl:',imgURL)
            #有夠白癡 line 傳送API不讓用函式呼叫
            line_bot_api = LineBotApi('QXOpsah7x1u7z32mpTd0Hnhv+XcbDxO3ua4HHrdxj9IWZA0Ow74ZdMa50AjeplzID6YMHxVUjVGQP/XzXEqbhCk4lL0QTzbAoSRRD/qGqKINvexHgeTgMSGGv7vI5/gzorNX761VhCjIZu3xjf8NgAdB04t89/1O/w1cDnyilFU=')
            yourID = 'U83b2468825f9b4c101039e594a9a8446'
            image_message = ImageSendMessage(
                original_content_url=str(imgURL),
                preview_image_url=str(imgURL)
            )
            line_bot_api.push_message(yourID, image_message)
            line_bot_api.push_message(yourID, TextSendMessage(text='有危險發生，類型:'+needReport))

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


app = Flask(__name__)
app.secret_key = 'sadkjahs'
#捕捉cam 或影片
video_capture = cv2.VideoCapture(0)
frame = None
frame_lock = threading.Lock()
should_capture_frame = False




#紀錄首頁
@app.route("/",methods=['GET'])
def getRecords():
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-009OG6J;'
                          'Database=homeSafty;'
                          'UID=sa;'
                          'PWD=123;')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM records ORDER BY time DESC')
    records = cursor.fetchall()
    # 關閉連接
    conn.close()
    return render_template("records.html",records=records)
    #return render_template("camStream.html")

#記錄 查看 編輯
@app.route('/detail/<int:id>' ,methods=['GET','POST'])
def detail(id):
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-009OG6J;'
                          'Database=homeSafty;'
                          'UID=sa;'
                          'PWD=123;')
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute('select * from records where id='+str(id))
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
        id=id
        name = request.form.get('name')
        opration = request.form.get('opration')
        sql = "UPDATE records SET "
        if name:
            sql += "name = '%s', " % name
        if opration:
            sql += "opration = '%s', " % opration
        # 去除最後一個逗號和空格
        sql = sql[:-2]
        sql += " WHERE id = %s" % id
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return redirect(url_for('detail', id=id))
    
#刪除紀錄
@app.route('/detailDelete/<int:id>/<path:Imgpath>' ,methods=['POST'])
def detailDelete(id,Imgpath):
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-009OG6J;'
                          'Database=homeSafty;'
                          'UID=sa;'
                          'PWD=123;')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE id = ?", id)
    conn.commit()
    conn.close()

    file_path = 'path_to_your_photo.jpg'

    try:
        os.remove(Imgpath)
        print("照片已成功刪除")
    except OSError as e:
        print(f"刪除照片時出現錯誤: {e}")
    return getRecords()
  


#鏡頭畫面 
def capture_frames():
    global frame, should_capture_frame
    while True:
        if should_capture_frame:
            ret, frame = video_capture.read()
            #辨識
            frame,needReport,name= yoloBulildForLocal.video_detection(frame)
            #通報
            alert(needReport,name,frame)
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
    

if __name__=="__main__":
    thread = threading.Thread(target=capture_frames)
    thread.start()
    app.run(host='0.0.0.0',debug=True)
    