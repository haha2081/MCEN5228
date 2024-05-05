import subprocess
import json
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
from openai import OpenAI



option2 = False
startup = True

def actual():
    process = subprocess.Popen(['python3', 'core.py'])

def train():
    process = subprocess.Popen(['python3', 'Facial Detection/train_model.py'], stdout=subprocess.PIPE)
    output = process.stdout.read()
    response = json.loads(output)

    return response['message']

def headshots(name):
    process = subprocess.Popen(['python3', 'Facial Detection/headshots.py'],
                                      stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            text=True)

    data_to_send = {"message": name}
    process.stdin.write(json.dumps(data_to_send))
    process.stdin.close()

    output = process.stdout.read()
    response = json.loads(output)

    return response['message']

def transcribe():
    process = subprocess.Popen(['python3', 'Mic/transcribe.py'],
                            stdout=subprocess.PIPE)
                        
    output = process.stdout.read()
    response = json.loads(output)

    return response['message']

def recordmic():
    process = subprocess.Popen(['python3', 'Mic/mic.py'],
                            stdout=subprocess.PIPE)
    output = process.stdout.read()
    response = json.loads(output)

    return response['message']

def process(message):
    data_to_send = {"message": message}

    process = subprocess.Popen(['python3', 'Think/think.py'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            text=True)

    process.stdin.write(json.dumps(data_to_send))
    process.stdin.close()

    output = process.stdout.read()
    response = json.loads(output)

    return response['message'] , response['state']

def talk(message):
    data_to_send = {"message": message}

    process = subprocess.Popen(['python3', 'Think/talk.py'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            text=True)

    process.stdin.write(json.dumps(data_to_send))
    process.stdin.close()

    output = process.stdout.read()
    response = json.loads(output)

    return response['state']

currentname = "unknown"
encodingsP = "Facial Detection/encodings.pickle"

data = pickle.loads(open(encodingsP, "rb").read())
cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()
    frame = imutils.resize(frame, width=500)
    boxes = face_recognition.face_locations(frame)
    encodings = face_recognition.face_encodings(frame, boxes)
    names = []

    for encoding in encodings:

        matches = face_recognition.compare_faces(data["encodings"],
			encoding)
        name = "Unknown" 

        if True in matches:
	
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            name = max(counts, key=counts.get)

            if currentname != name:
                currentname = name
                print(currentname)

        names.append(name)
        
        if startup:
            if len(names)>0:
                if len(names)==1 and name!='Unknown':
                    cap.release()
                    actual()

                if len(names)==1 and name == 'Unknown':
                    option2 = True
                    if option2:
                        message = f"You are a robotic assistant. You can see me, you don't know who I am and you want to ask my name."
                        response, state = process(message)
                        if state:
                            talk(response)
                            if recordmic():
                                name = process("Extract the name from this and output it only wihout anything else" + transcribe())
                                message = f"You are a robotic assistant. You just found out my name is {name}, can you ask me to move my head in all directions when you say now so you can take pictures for your facial detection dataset......... Now"
                                response, state = process(message)
                                if state:
                                    if talk(response):
                                        cap.release()
                                        if headshots(name[0]):
                                            message = f"You are a robotic assistant. You just finished trained a database on my face and my name is {name}."
                                            response, state = process(message)
                                            if state:
                                                talk(response)
                                                if train():
                                                    cap.release
                                                    actual()


                                    
                startup = False


    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break



cv2.destroyAllWindows()
cap.release()


