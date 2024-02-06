import cv2
import numpy as np
import time

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = cam.read()
    width = cam.get(3)
    height = cam.get(4)
    # print(height,width)
    splitFrame = np.zeros(frame.shape, np.uint8)
    frameResize = cv2.resize(frame, (int(width/2),int(height/2)))
    splitFrame[:int(height/2),:int(width/2)]=frameResize
    frameFlip0 = cv2.flip(frameResize,0)
    splitFrame[int(height/2):,:int(width/2)]=frameFlip0
    frameFlip1 = cv2.flip(frameResize,1)
    splitFrame[:int(height/2),int(width/2):]= frameFlip1
    frameFlip2 = cv2.flip(frameResize,-1)
    splitFrame[int(height/2):,int(width/2):]= frameFlip2
    cv2.imshow("Multiple outputs", splitFrame)

    cur_time = time.time()
    # print(cur_time)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()