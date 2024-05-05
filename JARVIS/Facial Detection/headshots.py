import cv2
import os
import sys
import json
import time

input_data = sys.stdin.read()
data = json.loads(input_data)


name = data['message'] #replace with your name

path = f'Facial Detection/dataset/{name}'
if not os.path.exists(path):
    os.makedirs(path)

cam = cv2.VideoCapture(0)

img_counter = 0
while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break

    img_name = 'Facial Detection/dataset/'+ name +f'/image_{img_counter}.jpg'
    cv2.imwrite(img_name, frame)
    img_counter += 1

    if img_counter>23:
        break
    
    time.sleep(0.35)

cam.release()

cv2.destroyAllWindows()


response_data = {"message": True}

# Send response to stdout
print(json.dumps(response_data))