import pyaudio
import numpy as np
from pydub import AudioSegment
from pydub.utils import make_chunks
import json 


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
SILENCE_THRESHOLD = 20 
SILENCE_DURATION = 1 

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
energies = []
calibration = False
frames = []
silent_frames = 0
is_silent = False

while True:
    data = stream.read(CHUNK)
    np_data = np.frombuffer(data, dtype=np.int16)
    energy = np.linalg.norm(np_data) / float(len(np_data))
    energies.append(energy)
    
    if len(energies)>15:
        SILENCE_THRESHOLD = np.mean(energies) + np.std(energies)
        calibration = True


    if energy < SILENCE_THRESHOLD:
        if not is_silent:
            is_silent = True
            silent_frames = 1
        else:
            silent_frames += 1
    else:
        is_silent = False
        silent_frames = 0
   
    frames.append(data)
   
    if silent_frames >= SILENCE_DURATION * RATE / CHUNK:
        break

stream.stop_stream()
stream.close()
p.terminate()

audio = b''.join(frames)
audio_segment = AudioSegment(data=audio, sample_width=p.get_sample_size(FORMAT), frame_rate=RATE, channels=CHANNELS)

audio_segment.export("recording.mp3", format="mp3")
response_data = {"message": True}

print(json.dumps(response_data))

