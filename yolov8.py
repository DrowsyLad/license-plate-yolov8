import cv2
from ultralytics import YOLO

#Load the Model
model_640 = YOLO('~/sis/best.pt')

print('data loaded')
print('oke')

BLACK = 0
RED = 1
WHITE = 2
YELLOW = 3

#camera
cam = cv2.VideoCapture('~/sis/angkot.mp4')
print('oke')

while True:
    ret, frame = cam.read()

    black, red, white, yellow = False, False, False, False
    print("detect")
    results = model_640(frame, imgsz=320)
    for result in results:
        frame = result.plot()
        for box in result.boxes:
            if box.cls[0] == BLACK:
                black = True
            if box.cls[0] == RED:
                red = True
            if box.cls[0] == WHITE:
                white = True
            if box.cls[0] == YELLOW:
                yellow = True

    if black: 
        print("Ada kendaraan pribadi")
    if white:
        print("Ada kendaraan pribadi")
    if yellow:
        print("Ada kendaraan angkutan umum")
    if red:
        print("Ada kendaraan instansi")
    if (black and red and yellow and white) is False:
        print("Tidak ada kendaraan")
        
    cv2.imshow('frame', cv2.resize(frame, (1000, 600)))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cam.release()
        cv2.destroyAllWindows()
        break
    #time.sleep(1)  
