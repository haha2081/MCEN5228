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


conversation = False
option2 = False
startup = True
previous_message = None
previous_response = None

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
                    message = f"You are a robotic assistant. Answer in a converstaion style. There are {len(names)} people starting at you, my name is {name}."
                    response, state = process(message)
                    if state:
                        talk(response)
                        previous_message = message
                        previous_response = response
                if len(names)>2 and len(names)<5:
                    message = f"You are a robotic assistant. Answer in a converstaion style. There are {len(names)} people starting at you, my name is {name}."
                    response, state = process(message)
                    if state:
                        talk(response)
                        previous_message = message
                        previous_response = response
                elif len(names) > 5:
                    message = f"You are a robotic assistant. Answer in a converstaion style. There are a lot of people starting at you (make a joke about being famous), my name is {name}."
                    response, state = process(message)
                    if state:
                        talk(response)  
                        previous_message = message
                        previous_response = response           
                startup = False
                conversation = True
        if conversation:
            if len(names)>0:
                if len(names)==1 and name!='Unknown':
                    message = f"You are a robotic assistant, my name is {name}, and my message is "
                    response, state = process(message)
                    if state:
                        talk(response)
                        previous_message = message
                        previous_response = response
                if len(names)>2 and len(names)<5:
                    message = f"You are a robotic assistant. Answer in a converstaion style. There are {len(names)} people starting at you, my name is {name}."
                    response, state = process(message)
                    if state:
                        talk(response)
                        previous_message = message
                        previous_response = response
                elif len(names) > 5:
                    message = f"You are a robotic assistant. Answer in a converstaion style. There are a lot of people starting at you (make a joke about being famous), my name is {name}."
                    response, state = process(message)
                    if state:
                        talk(response)  
                        previous_message = message
                        previous_response = response           
                startup = False
                conversation = True
        
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break



cv2.destroyAllWindows()
cap.release()


