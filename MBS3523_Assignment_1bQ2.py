import cv2

cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)
while True:
    ret, frame = cam.read()
    width = cam.get(3)
    height = cam.get(4)
    frameResize = cv2.resize(frame,(int(width/1.3),int(height/1.3)))
    frameCanny = cv2.Canny(frameResize, 100, 400)
    frameHSV = cv2.cvtColor(frameResize, cv2.COLOR_BGR2HSV)
    frameGray = cv2.cvtColor(frameResize, cv2.COLOR_BGR2GRAY)
    frameBlur = cv2.GaussianBlur(frameGray, (33, 33), 0)

    cv2.imshow('Webcam', frameResize)
    #cv2.imshow('Window Resize', frameResize)
    cv2.imshow("Webcam Canny Edges", frameCanny)
    cv2.imshow('Webcam HSV', frameHSV)
    cv2.imshow("Webcam Gaussian Blur", frameBlur)
    if cv2.waitKey(10) & 0xff == 27:
        break
cam.release()
cv2.destroyAllWindows()