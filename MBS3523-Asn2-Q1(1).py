import time
import cv2
import numpy as np

confThreshold = 0.4

cam = cv2.VideoCapture('walking_the_dogs.mp4')

# Create an empty list - classes[] and point the classesFile to 'coco.names'
classesFile = 'coco.names'
classes = []
# Load all classes in coco80.names into classes[]
with open(classesFile, 'r') as f:
    classes = f.read().splitlines()

# Load the configuration and weights file for YOLO-608
net = cv2.dnn.readNetFromDarknet('yolov3 (1).cfg','yolov3 (1).weights')
# Use OpenCV as backend and useCPU
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

frame_count = 0
start_time = time.time()

# Loop through each frame of the video
while True:
    success, img = cam.read()
    if not success:
        print("FPS:", frame_count / (time.time() - start_time))
        break

    height, width, ch = img.shape

    # Create a blob from the image and set it as the input to the network
    blob = cv2.dnn.blobFromImage(img, 1 / 255, (608, 608), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)

    output_layers_names = net.getUnconnectedOutLayersNames()
    LayerOutputs = net.forward(output_layers_names)

    bboxes = []  # array to store all bounding boxes of detected classes
    confidences = []  # array to store all confidence values of matching detected classes
    class_ids = []  # array to store all class IDs of matching detected classes

    # Iterate over each output layer and detect objects
    for output in LayerOutputs:
        for detection in output:
            scores = detection[5:]  # omit the first 5 values
            class_id = np.argmax(scores)  # find the highest score ID out of 80 values with the highest confidence value
            confidence = scores[class_id]
            if confidence > confThreshold:
                center_x = int(detection[0] * width)  # YOLO predicts centers of the image
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                bboxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-maximum suppression to remove overlapping bounding boxes
    indexes = cv2.dnn.NMSBoxes(bboxes, confidences, confThreshold, 0.4)

    font = cv2.FONT_HERSHEY_PLAIN
    colors = np.random.uniform(0, 255, size=(len(bboxes), 3))
    n = 0
    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = bboxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i], 2))
            color = colors[i]
            if label == 'keyboard':
                n += 1
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label + " " + "[" + str(n) + "]  " + confidence, (x, y + 20), font, 1, (255, 255, 255), 2)
                cv2.putText(img, "There are: " + str(n) + " " + label, (200, 30),
                            font, 2, (0, 0, 255), 2)

    cv2.imshow('Image', img)
    frame_count += 1

    if cv2.waitKey(1) & 0xff == 27:
        break

cam.release()

cv2.destroyAllWindows()