import cv2
import mediapipe as mp
import time

# Function to calculate the distance between two points
def calculate_distance(a, b):
    return ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Initialize Mediapipe Hands model
mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils
hands = mpHands.Hands(max_num_hands=2, min_detection_confidence=0.8, min_tracking_confidence=0.6)

# Time for FPS calculation
t_old = 0
t_new = 0

# Variables for counting peace gestures
gesture_detected = False
counter = 0

while True:
    success, img = cam.read()
    if not success:
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Make detection
    results = hands.process(imgRGB)

    imgRGB.flags.writeable = True
    img = cv2.cvtColor(imgRGB, cv2.COLOR_RGB2BGR)

    # Extract landmarks and draw hand landmarks
    if results.multi_hand_landmarks:
        for handLandmarks in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLandmarks, mpHands.HAND_CONNECTIONS,
                                  mpDraw.DrawingSpec(color=(125, 0, 125), thickness=2, circle_radius=4),
                                  mpDraw.DrawingSpec(color=(255, 0, 255), thickness=2, circle_radius=2))

            # Get landmarks for middle finger and index finger
            middle_finger = (handLandmarks.landmark[12].x, handLandmarks.landmark[12].y)
            index_finger = (handLandmarks.landmark[8].x, handLandmarks.landmark[8].y)

            # Calculate distance between middle finger and index finger
            distance = calculate_distance(middle_finger, index_finger)

            # Determine gesture state
            if distance < 0.1:  # Adjust this threshold as needed
                if not gesture_detected:
                    gesture_detected = True
                    counter += 1  # Increment counter when peace gesture is detected
            else:
                gesture_detected = False

    cv2.putText(img, f"Peace Gestures: {counter}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    t_new = time.time()
    fps = 1 / (t_new - t_old)
    t_old = t_new
    cv2.putText(img, 'FPS: ' + str(int(fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Peace Gesture Counter', img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cam.release()
cv2.destroyAllWindows()