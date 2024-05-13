import cv2
import numpy as np

confThreshold = 0.8  # Confidence threshold
fruit_prices = {"apple": 1, "banana": 2.5, "orange": 3.5}
fruit_classes = ['apple', 'banana', 'orange']
fruit_colors = {"apple": (0, 255, 0), "banana": (0, 255, 255), "orange": (0, 165, 255)}

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Load COCO classes
classesFile = 'coco.names'
with open(classesFile, 'r') as f:
    classes = f.read().splitlines()

# Load YOLO model
net = cv2.dnn.readNetFromDarknet('yolov3 (1).cfg', 'yolov3 (1).weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

while True:
    success, img = cam.read()
    height, width, ch = img.shape

    # Reset fruit counts for each frame
    fruit_counts = {"apple": 0, "banana": 0, "orange": 0}
    total_price = 0

    blob = cv2.dnn.blobFromImage(img, 1 / 255, (320, 320), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)

    layerNames = net.getLayerNames()
    output_layers_names = net.getUnconnectedOutLayersNames()
    LayerOutputs = net.forward(output_layers_names)

    bboxes = []
    confidences = []
    class_ids = []

    for output in LayerOutputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > confThreshold and classes[class_id] in fruit_classes:  # Check if detected object is a fruit
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                bboxes.append([x, y, w, h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(bboxes, confidences, confThreshold, 0.4)

    font = cv2.FONT_HERSHEY_PLAIN
    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = bboxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i], 2))
            color = fruit_colors[label] if label in fruit_colors else (0, 0, 255)  # Red color for unknown fruits

            # Draw bounding box
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

            # Draw fruit name and confidence
            cv2.putText(img, label + " " + confidence, (x, y + 20),
                        font, 1, (255, 255, 255), 1)

            # Update fruit counts
            fruit_counts[label] += 1

            #Calculate total price
            total_price += fruit_prices.get(label, 0)

            # Draw bounding box for fruit name
            cv2.rectangle(img, (x, y - 30), (x + len(label) * 12, y), color, -1)
            cv2.putText(img, label, (x, y - 10), font, 1, (0, 0, 0), 1)  # Change text color to black

    else:
        # Display "No Fruit Detected" message on top left corner
        cv2.putText(img, "No Fruit Detected", (50, 50), font, 1.5, (0, 0, 255), 2)

    # Display fruit counts and total price on upper right corner
    fruit_text = ", ".join([f"{count} {fruit}" for fruit, count in
                            fruit_counts.items() if count > 0])
    cv2.putText(img, "Fruit Counts: " + fruit_text, (width -600, 60), font, 1, (255, 0, 0), 2)
    price_text = " + ".join([f"{count} {fruit}" for fruit, count in
                             fruit_counts.items()])
    cv2.putText(img, f"Total Price: {price_text} = ${total_price:.2f}", (width - 600, 120), font, 1, (255, 0, 0), 2)

    cv2.imshow('Image', img)

    if cv2.waitKey(1) & 0xff == 27:
        break

cam.release()
cv2.destroyAllWindows()