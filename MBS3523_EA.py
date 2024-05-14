import cv2
import mediapipe as mp
import time
import random
import pygame

# Set the initial speed range for the ball's flight
min_speed = -10
max_speed = 10

# Initialize hand tracking
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize game variables
paddle_x = 0
paddle_y = 0
ball_x = 0
ball_y = 0
ball_speed_x = 2
ball_speed_y = 2
score = 0
collision = False
paddle_color = (0, 255, 0)  # Initial color of the paddle
hit_count = 0  # Number of successful hits
last_hit_time = time.time()

# Initialize pygame
pygame.init()

# Load background music
pygame.mixer.music.load("better-day-186374.mp3")
pygame.mixer.music.set_volume(0.5)  # Set the music volume

# Load sound effect
collision_sound = pygame.mixer.Sound("doorhit-98828.mp3")

# Play background music
pygame.mixer.music.play(-1)  # -1 means looping the music indefinitely


# Define the hand tracking callback function
def hand_tracking_callback(image, results):
    global paddle_x, paddle_y

    # Check if hands are detected
    if results.multi_hand_landmarks:
        # Get the position of the first hand's index finger
        hand_landmarks = results.multi_hand_landmarks[0]
        index_finger_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

        # Convert the position to pixel coordinates
        image_height, image_width, _ = image.shape
        paddle_x = int(index_finger_landmark.x * image_width)
        paddle_y = int(index_finger_landmark.y * image_height)


# Initialize video capture
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Initialize hand tracking
with mp_hands.Hands(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
) as hands:
    # Read the first frame to get its dimensions
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Failed to read video capture")

    frame_height, frame_width, _ = frame.shape

    # Set the initial position of the ball to the center of the frame
    ball_x = frame_width // 2
    ball_y = frame_height // 2
    # Set the initial direction of the ball's flight
    ball_speed_x = 2  # Positive value for rightward movement
    ball_speed_y = -2  # Negative value for upward movement

    # Start the game loop
    while cap.isOpened():
        # Generate random values for ball_speed_x and ball_speed_y
        ball_speed_x = random.uniform(min_speed, max_speed)
        ball_speed_y = random.uniform(min_speed, max_speed)
        # Read frame from video capture
        # Update the ball's position based on the generated speed values
        ball_x += ball_speed_x
        ball_y += ball_speed_y
        ret, frame = cap.read()

        if not ret:
            break

        # Flip the frame horizontally for a mirror-like effect
        frame = cv2.flip(frame, 1)

        # Convert the frame to RGB for hand tracking
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with hand tracking
        results = hands.process(image)

        # Update the paddle position based on hand tracking
        hand_tracking_callback(frame, results)

        # Update the ball position
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Check ball collision with walls
        if ball_x <= 0 or ball_x >= frame_width - 10:
            # Regenerate a new ball
            ball_x = frame_width // 2
            ball_y = frame_height // 2
            ball_speed_x = 2
            ball_speed_y = 2

        if ball_y <= 0 or ball_y >= frame_height - 10:
            # Regenerate a new ball
            ball_x = frame_width // 2
            ball_y = frame_height // 2
            ball_speed_x = 2
            ball_speed_y = 2

        # Check ball collision with paddle
        if (
                ball_x >= paddle_x
                and ball_x <= paddle_x + 100
                and ball_y >= paddle_y
                and ball_y <= paddle_y + 20
        ):
            if not collision:
                ball_speed_y *= -1
                score += 1
                # Play the collision sound effect
                collision_sound.play()

                # Update the hit count and last hit time
                hit_count += 1
                last_hit_time = time.time()

                # Change the color of the paddle
                paddle_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                collision = True
        else:
            collision = False
            # Check if 5 seconds have passed since the last hit
            if time.time() - last_hit_time > 5:
                # Prompt the user to reset the game
                cv2.putText(
                    frame,
                    "All the stress is gone! Press 'R' to reset.",
                    (frame_width // 2 - 300, frame_height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
                if cv2.waitKey(1) & 0xFF == ord("r"):
                    # Reset the game
                    ball_x = frame_width // 2
                    ball_y = frame_height // 2
                    ball_speed_x = 2
                    ball_speed_y = 2
                    score = 0
                    collision = False
                    paddle_color = (0, 255, 0)  # Initial color of the paddle
                    hit_count = 0
                    last_hit_time = time.time()

        # Draw the paddle and ball on the frame
        cv2.rectangle(
            frame,
            (paddle_x, paddle_y),
            (paddle_x + 100, paddle_y + 20),
            paddle_color,
            cv2.FILLED,
        )
        cv2.circle(frame, (int(ball_x), int(ball_y)), 10, (255, 0, 0), cv2.FILLED)

        # Display the score on the frame
        cv2.putText(
            frame,
            f"Score: {score}",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )

        # Display the frame
        cv2.imshow("Frame", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the video capture and close all windows
    cap.release()
    cv2.destroyAllWindows()