import cv2
import numpy as np
import serial

# Default HSV values for light green color
default_lowH, default_lowS, default_lowV = 40, 50, 50
default_highH, default_highS, default_highV = 80, 255, 255

# Initialize serial communication with Arduino
ser = serial.Serial('COM4', 115200)

# Function to update HSV values based on trackbar positions
def update_HSV_values(lowH, lowS, lowV, highH, highS, highV):
    global lowerBound, upperBound
    lowerBound = np.array([lowH, lowS, lowV])
    upperBound = np.array([highH, highS, highV])

# Function to move camera servo based on centroid position
def move_camera_servo(centroid_x, centroid_y, frame_width, frame_height):
    panAngle = int(centroid_x * 180 / frame_width)  # Map centroid_x to 0-180 range
    tiltAngle = int(centroid_y * 180 / frame_height)  # Map centroid_y to 0-180 range
    panAngle = min(max(panAngle, 0), 180)  # Ensure panAngle is within 0-180 range
    tiltAngle = min(max(tiltAngle, 0), 180)  # Ensure tiltAngle is within 0-180 range
    ser.write(f"{panAngle},{tiltAngle}\r".encode())  # Send servo angles to Arduino
    print(f"Sent servo angles to Arduino: Pan={panAngle}, Tilt={tiltAngle}")

# Initialize webcam
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cam.isOpened():
    print("Error: Cannot open webcam")
    exit()

# Create window for controlling HSV values
cv2.namedWindow("Control HSV")
cv2.createTrackbar("LowH", "Control HSV", default_lowH, 179, lambda x: None)
cv2.createTrackbar("HighH", "Control HSV", default_highH, 179, lambda x: None)
cv2.createTrackbar("LowS", "Control HSV", default_lowS, 255, lambda x: None)
cv2.createTrackbar("HighS", "Control HSV", default_highS, 255, lambda x: None)
cv2.createTrackbar("LowV", "Control HSV", default_lowV, 255, lambda x: None)
cv2.createTrackbar("HighV", "Control HSV", default_highV, 255, lambda x: None)

while True:
    # Capture frame from webcam
    ret, frame = cam.read()
    if not ret:
        print("Error: Cannot read frame")
        break

    # Convert frame from BGR to HSV color space
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get current trackbar positions
    lowH = cv2.getTrackbarPos("LowH", "Control HSV")
    highH = cv2.getTrackbarPos("HighH", "Control HSV")
    lowS = cv2.getTrackbarPos("LowS", "Control HSV")
    highS = cv2.getTrackbarPos("HighS", "Control HSV")
    lowV = cv2.getTrackbarPos("LowV", "Control HSV")
    highV = cv2.getTrackbarPos("HighV", "Control HSV")

    # Update HSV values
    update_HSV_values(lowH, lowS, lowV, highH, highS, highV)

    # Threshold the HSV frame to get only the desired color object
    mask = cv2.inRange(hsvFrame, lowerBound, upperBound)

    # Apply mask to the original frame
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If contours are found, calculate centroid and adjust servos
    if contours:
        # Get largest contour
        largestContour = max(contours, key=cv2.contourArea)

        # Get bounding rectangle around the largest contour
        x, y, w, h = cv2.boundingRect(largestContour)

        # Draw rectangle around the detected object
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Calculate centroid of the largest contour
        centroid_x = x +w // 2
        centroid_y = y + h // 2

        # Move camera servo to track the object
        move_camera_servo(centroid_x, centroid_y, frame.shape[1], frame.shape[0])

    # Display the original frame with the object highlighted
    cv2.imshow("Webcam", frame)

    # Display the masked frame in the HSV controlling window
    cv2.imshow("Control HSV", result)

    # Create a black image
    black_image = np.zeros(frame.shape, dtype=np.uint8)

    # Set pixels in the black image to white where light green color is detected
    black_image[mask == 255] = (255, 255, 255)

    # Display the black and white image with light green color detected
    cv2.imshow("Detected Color", black_image)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cam.release()
cv2.destroyAllWindows()