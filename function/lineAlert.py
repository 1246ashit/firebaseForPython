from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.models import ImageSendMessage
import time
from cloudinary.uploader import upload
import cloudinary
from cloudinary.utils import cloudinary_url

def uploadimg(imagePath):
    # Import
    # Config
    cloudinary.config(
    cloud_name = "dxcyu5nun",
    api_key = "745267353199922",
    api_secret = "Ar6PM_E5cUsZRii8m3GjqJNufEc",
    secure = True
    )
# Upload
    response =upload(imagePath)
    image_url = response['secure_url']
    public_id = response['public_id']
    return image_url

def buildLineConn():
    line_bot_api = LineBotApi('QXOpsah7x1u7z32mpTd0Hnhv+XcbDxO3ua4HHrdxj9IWZA0Ow74ZdMa50AjeplzID6YMHxVUjVGQP/XzXEqbhCk4lL0QTzbAoSRRD/qGqKINvexHgeTgMSGGv7vI5/gzorNX761VhCjIZu3xjf8NgAdB04t89/1O/w1cDnyilFU=')
    yourID = 'U83b2468825f9b4c101039e594a9a8446'

    image_message = ImageSendMessage(
        original_content_url='https://res.cloudinary.com/dxcyu5nun/image/upload/v1684287498/tih0jelx4qsropx5srcx.jpg',
        preview_image_url='https://res.cloudinary.com/dxcyu5nun/image/upload/v1684287498/tih0jelx4qsropx5srcx.jpg'
        )
    line_bot_api.push_message(yourID, image_message)
    line_bot_api.push_message(yourID, TextSendMessage(text='有危險發生'))