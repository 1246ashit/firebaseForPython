import function.yoloBulildForLocal as yoloBulildForLocal
import cv2
video_capture = cv2.VideoCapture('testMaterial/room_fire2.mov.mp4')

while True:
    ret, frame = video_capture.read()  
    frame,needReport,name= yoloBulildForLocal.video_detection(frame)
    cv2.imshow('Video', frame)  

    if cv2.waitKey(1) & 0xFF == ord('q'):  
        break

video_capture.release()  
cv2.destroyAllWindows()  

