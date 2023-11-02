import cv2
from ultralytics import YOLO
import serial
import time

#Load the Model
detect = YOLO('best.pt')

BLACK = 0
RED = 1
WHITE = 2
YELLOW = 3

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600

prev_frame_time = time.time()

#camera
cam = cv2.VideoCapture('angkot-1.mp4')

#serial handler
handler = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

gate_status = "Closed"

def debug_vision(frame, status:str):
    global prev_frame_time
    new_frame_time = time.time() 
    fps = 1/(new_frame_time-prev_frame_time) 
    prev_frame_time = new_frame_time 
    cv2.putText(frame, str("Status: " + status), (int(10), int(16)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)  
    cv2.putText(frame, str("FPS: " + str(round(fps, 1))), (int(10), int(32)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)  
    return frame

while True:
    ret, frame = cam.read()
    if frame is None:
        print("Video ended or Camera disconnected. Exiting...")
        break

    black, red, white, yellow = False, False, False, False
    closest, biggest_y = None, 0
    results = detect(frame, imgsz=320)
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
        cam.release()
        cv2.destroyAllWindows()
        break
    #time.sleep(1)  