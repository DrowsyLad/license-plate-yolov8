import cv2
from ultralytics import YOLO
import serial
import time
import os
import argparse

BLACK = 0
RED = 1
WHITE = 2
YELLOW = 3

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600

INFERENCE_SIZE = 480

prev_frame_time = time.time()

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename')
parser.add_argument('-v', '--videoid')
args = parser.parse_args()
print("filename: {}, video id: {}".format(args.filename, args.videoid))

#Load the Model
print("Loading model with {}px inference size...".format(INFERENCE_SIZE))
detect = YOLO('yolov8-epoch100.pt')
print("Success")

#camera
print("Initializing source...")
video_default = 'angkot-1.mp4'
if args.filename is not None:
    video = args.filename
    if os.path.exists(video) is False:
        print("File "+video+" not found")
        video = video_default
elif args.videoid is not None:
    video = "video-"+str(args.videoid)+".mp4"
    if os.path.exists(video) is False:
        print("File "+video+" not found")
        video = video_default
else:
    video = video_default
camera = None
source = None

for index in range (0,2):
    if os.path.exists('/dev/video'+str(index)):
        camera = index
        print("Camera found. Using /dev/video"+str(camera))
        break

if camera is None:
    print("Error loading camera. Switching to video...")
    source = cv2.VideoCapture(video)
    print("Using video file "+video)
else:
    source = cv2.VideoCapture(camera)

#serial handler
print("Initializing serial handler...")
handler = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
print("Success")

gate_status = "Closed"

def debug_vision(frame, status:str):
    global prev_frame_time
    new_frame_time = time.time() 
    fps = 1/(new_frame_time-prev_frame_time) 
    prev_frame_time = new_frame_time 
    cv2.putText(frame, str("Status: " + status), (int(10), int(32)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1)  
    cv2.putText(frame, str("FPS: " + str(round(fps, 1))), (int(10), int(64)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1)  
    return frame

print("Initializing detector...")

while True:
    ret, frame = source.read()
    
    if frame is None:
        print("Video ended or Camera disconnected. Exiting...")
        break

    # frame = cv2.resize(frame, (INFERENCE_SIZE, INFERENCE_SIZE))

    black, red, white, yellow = False, False, False, False
    closest, biggest_y = None, 0
    results = detect(frame, imgsz=INFERENCE_SIZE, stream=True)
    for result in results:
        frame = result.plot()
        for box in result.boxes:
            _, y1, _, y2 = box.xyxy[0]
            if (y1+y2)/2 > biggest_y:
                closest = box.cls[0]
            if box.cls[0] == BLACK:
                black = True
            if box.cls[0] == RED:
                red = True
            if box.cls[0] == WHITE:
                white = True
            if box.cls[0] == YELLOW:
                yellow = True
        break

    if black: 
        print("Ada kendaraan pribadi")
    if white:
        print("Ada kendaraan pribadi")
    if yellow:
        print("Ada kendaraan angkutan umum")
    if red:
        print("Ada kendaraan instansi")
    if (black or red or yellow or white) is False:
        print("Tidak ada kendaraan")

    if closest is None:
        handler.write(bytes("g90", 'ascii')) #open
        gate_status = "Open"
    elif closest == YELLOW:
        handler.write(bytes("r0", 'ascii')) #close
        gate_status = "Closed"
    else:
        handler.write(bytes("g90", 'ascii')) #open
        gate_status = "Open"

    frame = debug_vision(frame, gate_status)

    cv2.imshow('frame', cv2.resize(frame, (1000, 600)))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        source.release()
        cv2.destroyAllWindows()
        break
    #time.sleep(1)  
