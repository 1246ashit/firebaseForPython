import uuid
import cv2
from imgurpython import ImgurClient
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import Services.CallSql as CallSql
import datetime

handler = WebhookHandler('51aeadc5c1eb9f92d3c777e2a6be34f9')
line_bot_api = LineBotApi('QXOpsah7x1u7z32mpTd0Hnhv+XcbDxO3ua4HHrdxj9IWZA0Ow74ZdMa50AjeplzID6YMHxVUjVGQP/XzXEqbhCk4lL0QTzbAoSRRD/qGqKINvexHgeTgMSGGv7vI5/gzorNX761VhCjIZu3xjf8NgAdB04t89/1O/w1cDnyilFU=')

#把照片傳去imgur
def imgurUpload(img):
    client_id = '1830a43cdfc9598'
    client_secret = '6994d0ac3591f69b24de8807bf503ac0f3088e4e'
    #path="function/faceData/Chagy.jpg"
    client = ImgurClient(client_id, client_secret).upload_from_path(img, config=None, anon=True)#上傳 
    #print(client["link"])#輸出照片
    return client["link"]

def alert(reportType,name,frame):
    global line_bot_api
    if len(reportType)!=0:
        # 如果警告未觸發，則觸發警告並設定冷卻時間
        print("偵測到危險!")
        # 儲存相片
        random_uuid = uuid.uuid4()
        photo_address=str(random_uuid)+'.jpg'
        cv2.imwrite("./static/photo/saveData/"+photo_address, frame)
        #line 警報
        imgURL=imgurUpload("./static/photo/saveData/"+photo_address)
        print('imgurl:',imgURL)
        #line 傳送API
        image_message = ImageSendMessage(
                original_content_url=str(imgURL),
                preview_image_url=str(imgURL)
                )
        for i in CallSql.fatchAllUser():
            print(i.userId)
            line_bot_api.push_message(i.userId, image_message)
            line_bot_api.push_message(i.userId, TextSendMessage(text='有危險發生，類型:'+str(reportType)))

            # 取得現在的日期
            current_time = datetime.datetime.now()
            CallSql.SaveInSql(current_time,name,photo_address,reportType)
        return True
    return False