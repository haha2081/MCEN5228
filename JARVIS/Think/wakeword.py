import pyaudio
import numpy as np
from pydub import AudioSegment
from pydub.utils import make_chunks
from openai import OpenAI
from playsound import playsound
from pathlib import Path
import os
from random import randint

responses = ['Uh huh', 'Yes ?', 'You called for me?','What do you want?', 'What\'s up ?', 'Tell me', 'What is it you need' ]

client = OpenAI(api_key='') #input ur api here

def record():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    SILENCE_THRESHOLD = 30 
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


def transcribe():
    file= open("recording.mp3", "rb")
    translation = client.audio.translations.create(
    model="whisper-1", 
    file=file
    )
    return translation.text

def think(message):
  stream = client.chat.completions.create(
      model="gpt-4",
      messages=[{"role": "system", "content": 'You are a wakeword detector, listening for the word Jarvis, return True or False'}, 
                {"role": "user", "content": message}],
      stream=False,
  )
  return stream.choices[0].message.content


def play_text(message):
  speech_file_path = Path(__file__).parent / "speech.mp3"
  response = client.audio.speech.create(
    model="tts-1",
    voice="fable",
    input=message
)
  response.stream_to_file(speech_file_path)

  playsound(speech_file_path)

while True: 

    record()
    message = transcribe()
    thought = think(message)
    if thought:
        rando = randint(0, len(responses))
        print(rando)
        play_text(responses[rando])
        break
      
    os.remove('recording.mp3')
