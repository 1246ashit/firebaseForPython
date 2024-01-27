import Services.CallSql as CallSql
from flask import(Flask,render_template,
                  Response,request,
                  abort
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
from Controller.Cam import CamBP

app=Flask(__name__,static_folder='static')
app.config.from_object('config')

app.register_blueprint(settingsBP, url_prefix='/Settings')
app.register_blueprint(InformationBP)
app.register_blueprint(CamBP)

# 必須放上自己的Channel Access Token
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



#主程式
import os
if __name__ == "__main__":
    # 啟動 ngrok 隧道
    print("ngrok 隧道 URL:",public_url)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)