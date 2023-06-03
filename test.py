#載入LineBot所需要的套件
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import re
import pyodbc

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('QXOpsah7x1u7z32mpTd0Hnhv+XcbDxO3ua4HHrdxj9IWZA0Ow74ZdMa50AjeplzID6YMHxVUjVGQP/XzXEqbhCk4lL0QTzbAoSRRD/qGqKINvexHgeTgMSGGv7vI5/gzorNX761VhCjIZu3xjf8NgAdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('51aeadc5c1eb9f92d3c777e2a6be34f9')

#取得所有使用者的ID
def lineUserComfirm(): 
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-009OG6J;'
                          'Database=homeSafty;'
                          'UID=sa;'
                          'PWD=123;')
    cursor = conn.cursor()
    sql = "SELECT user_id FROM LineUserId "
    cursor.execute(sql)
    userIds = cursor.fetchall()
    cursor.commit()
    # 關閉連接
    conn.close()
    return userIds

#對所有人傳訊息
for i in lineUserComfirm():
    print(i.user_id)
    line_bot_api.push_message(i.user_id, TextSendMessage(text='系統開啟'))

#儲存新的line userId
def IdSaveInSql(userId):
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-009OG6J;'
                          'Database=homeSafty;'
                          'UID=sa;'
                          'PWD=123;')
    cursor = conn.cursor()
    data=(userId)
    sql = "INSERT INTO LineUserId  (user_id) VALUES ( ? )"
    cursor.execute(sql,data)
    cursor.commit()
    # 關閉連接
    conn.close()
    print("儲存成功")
#line user確認是否有登入
def lineUserComfirm(userId): 
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-009OG6J;'
                          'Database=homeSafty;'
                          'UID=sa;'
                          'PWD=123;')
    cursor = conn.cursor()
    sql = "SELECT id FROM LineUserId WHERE user_id = ?"
    cursor.execute(sql,userId)
    records = cursor.fetchall()
    cursor.commit()
    # 關閉連接
    conn.close()
    if len(records) == 0:
        print('未登入之ID，執行登入')
        IdSaveInSql(userId)

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
    if re.match('告訴我秘密',message):
        line_bot_api.reply_message(event.reply_token,TextSendMessage('才不告訴你哩！'))
        print("剛剛傳了訊息")
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(message))

@handler.add(FollowEvent)
def handle_follow(event):
    UserId = event.source.user_id
    print(UserId)
    # 在這裡處理使用者加入事件
    line_bot_api.reply_message(event.reply_token,TextSendMessage('歡迎使用居家辨識系統'))
    lineUserComfirm(UserId)
    print("新的成員加入")

#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)