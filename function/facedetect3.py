import face_recognition
import os, sys
import cv2
import numpy as np
import math

face_locations = []
face_encodings = []
face_names = []
known_face_encodings = []
known_face_names = []

#臉部信心值
def face_confidence(face_distance, face_match_threshold=0.5):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'

#建立模組
def encodeFaces(route):
        print("開始建立模型")
        for image in os.listdir(route):
            face_image = face_recognition.load_image_file(f"faces/{image}")
            face_encoding = face_recognition.face_encodings(face_image)[0]

            known_face_encodings.append(face_encoding)
            known_face_names.append(image[:-4])
        print("建立模型完成")
#預測
def runRecognition(img):
    # 將圖片resize 變成原本的80%
    small_frame = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    # 把圖片從BGR 轉去RGB
    rgb_small_frame =  cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    # 在當前的圖片找到臉的位置並編碼
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "???"
        confidence = '???'

        # 確定是誰的臉以及信心值處理
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            confidence = face_confidence(face_distances[best_match_index])

        face_names.append(f'{name} ({confidence})')
    return face_names, face_locations


#畫出位置，名子，信心值
def drawInImg(img,face_locations,face_names):
    for (top, right, bottom, left), name in zip(face_locations,face_names):
                # 變回原來大小
                top *= 2
                right *= 2
                bottom *= 2
                left *= 2

                # Create the frame with the name
                cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(img, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
    return img