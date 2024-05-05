
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2

currentname = "unknown"
encodingsP = "Facial Detection/encodings.pickle"

print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())
vs = VideoStream(src=0,framerate=10).start()
time.sleep(2.0)

fps = FPS().start()

while True:

	frame = vs.read()
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
		print(names)
		print(name)

	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		break

	fps.update()

fps.stop()

cv2.destroyAllWindows()
vs.stop()


