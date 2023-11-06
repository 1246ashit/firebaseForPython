#6994d0ac3591f69b24de8807bf503ac0f3088e4e


from imgurpython import ImgurClient

def imgurUpload(img):
    client_id = '1830a43cdfc9598'
    client_secret = '6994d0ac3591f69b24de8807bf503ac0f3088e4e'
    #path="function/faceData/Chagy.jpg"
    client = ImgurClient(client_id, client_secret).upload_from_path(img, config=None, anon=True)#上傳 
    #print(client["link"])#輸出照片
    return client["link"]




