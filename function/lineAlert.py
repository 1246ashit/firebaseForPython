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
# 上傳
    response =upload(imagePath)
    image_url = response['secure_url']
    public_id = response['public_id']
    return image_url
