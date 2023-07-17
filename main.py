import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from tracker import*
import cvzone
import serial.tools.list_ports


model=YOLO('yolov8n.pt')

# Set confidence threshold to 0.5 (default is 0.25)
model.conf = 0.5

# Setting up serial communication with COM6
ports= serial.tools.list_ports.comports()
serialInst = serial.Serial()
serialInst.baudrate = 9600
serialInst.port = 'COM6'
serialInst.open()

# Define a function to send the target point in the correct format
def servoPos(x,y):
    x = 180 - ((x/800)*180)
    y = (y/800)*180
    X = str(int(x))
    Y = str(int(y))
    result = X + ',' + Y + '.'
    return(result)

# Capture video frames
cap=cv2.VideoCapture(0)

ids = []

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n") 
person_id = class_list.index('person')

count=0
persondown={}
tracker=Tracker()
counter1=[]

personup={}
counter2=[]
cy1=194
cy2=220
offset=6

i = 0
object_centroids = {}

while True: 

    ret,frame = cap.read()
    if not ret:
        break

    count += 1
    if count % 3 != 0:
        continue

    frame=cv2.resize(frame,(800,800))
    results=model.predict(frame)
    a=results[0].boxes.data
    px=pd.DataFrame(a).astype("float")
    list=[]

    for index,row in px.iterrows():
        x1=int(row[0])
        y1=int(row[1])
        x2=int(row[2])
        y2=int(row[3])
        d=int(row[5])
        conf=float(row[4])

        if conf >= model.conf and d == person_id:
            list.append([x1,y1,x2,y2])
    bbox_id=tracker.update(list)

    ids = []

    for bbox in bbox_id:
        x3,y3,x4,y4,id=bbox
        ids.append(id)
        cx=int(x3+x4)//2
        cy=int(y3+y4)//2
        cv2.circle(frame,(cx,cy),4,(255,0,255),-1)

    sorted_ids = sorted(ids)
    
    if i >= len(sorted_ids):
        i = len(sorted_ids)-1

    for bbox in bbox_id:
        x3, y3, x4, y4, id = bbox
        cx = int(x3 + x4) // 2
        cy = int(y3 + y4) // 2

        if id not in object_centroids:
            object_centroids[id] = (cx, cy)
        else:
            object_centroids[id] = (0.5 * cx + 0.5 * object_centroids[id][0], 0.5 * cy + 0.5 * object_centroids[id][1])

    # Send the centroid of the selected object over serial
    if sorted_ids and sorted_ids[i] in object_centroids:
        cx, cy = object_centroids[sorted_ids[i]]
        serialInst.write(servoPos(cx, cy).encode('utf-8'))
        serialInst.flush()

    else:
        cv2.rectangle(frame, (x3,y3), (x4,y4), (0,255,0), 2)
        cv2.putText(frame, str(id), (x3,y3), cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0), 2)
        serialInst.write(" ".encode('utf-8'))
        serialInst.flush()

    if (id == sorted_ids[i]):
            cv2.rectangle(frame, (x3,y3), (x4,y4), (0,0,255), 2)

    else:
        cv2.rectangle(frame, (x3,y3), (x4,y4), (0,255,0), 2)
        
    cv2.imshow("RGB", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('.'):
        i += 1
    elif key == ord(','):
        i -= 1
    if (i < 0):
        i = 0

    