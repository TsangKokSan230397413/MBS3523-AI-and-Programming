import serial
import cv2

ser = serial.Serial('COM4', 9600)

cv2.namedWindow("DHT22 Data")

cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)

while True:
    data = ser.readline().decode().strip()
    ret, frame = cam.read()

    cv2.putText(frame, data, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 255, 255), 3)

    cv2.imshow("DHT22 Data", frame)

    if cv2.waitKey(1) & 0xff == 27:
        break

ser.close()
cam.release()
cv2.destroyAllWindows()
