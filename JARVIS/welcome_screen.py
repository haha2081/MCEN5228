import pygame
import sys
from pygame.locals import FULLSCREEN, QUIT, SRCALPHA, BLEND_RGBA_MULT
import arabic_reshaper
from bidi.algorithm import get_display
import time
import pyaudio
import numpy as np
from pydub import AudioSegment
from pydub.utils import make_chunks
from openai import OpenAI
from playsound import playsound
from pathlib import Path
import os
from random import randint
import librosa
import soundfile
import json

input_data = sys.stdin.read()
data = json.loads(input_data)
name = data['message']

responses = ['Uh huh', 'Yes ?', 'You called for me?','What do you want?', 'What\'s up ?', 'Tell me', 'What is it you need' ]

client = OpenAI(api_key='') #Input ur API key here

def record(name):
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

    print(f'{name}.mp3')

    audio_segment.export(f'{name}.mp3', format="mp3")


def transcribe(name):
    file= open(f'{name}.mp3', "rb")
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

def convo(history):
 
    stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "system", "content": f'You are a robotic assistant, your name is jarvis and my name is {name} , keep your answers short'}, 
                {"role": "user", "content": history}],

    stream=False,
    )
    return stream.choices[0].message.content


def play_text(message, name):
  speech_file_path = Path(__file__).parent / f'{name}.wav'
  response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=message
)
  response.stream_to_file(speech_file_path)
  y, sr = librosa.load(speech_file_path)
  steps = 0
  y_third = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)
  soundfile.write(speech_file_path, y_third, sr)
  playsound(speech_file_path)


#####################################################PYGAME################################################################
# Initialize Pygame
pygame.init()

# Screen settings
infoObject = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((0, 0), FULLSCREEN)

# Colors
BLUE, BLACK, WHITE, GREEN = (0, 128, 255), (0, 0, 0), (255, 255, 255), (57, 255, 20)

# Text settings
WELCOME_MESSAGES = ["Welcome to Jarvis", "Bienvenue à Jarvis", "مرحبا بكم في جارفيس",
                    "Bem vindo ao Jarvis", "欢迎来到贾维斯"]
FONT_SIZE = 40
FONT_PATHS = ['Display/Amiri/Amiri-Bold.ttf'] * (len(WELCOME_MESSAGES) - 1) + ['Display/Noto_Sans_SC/static/NotoSansSC-Regular.ttf']
fonts = [pygame.font.Font(path, FONT_SIZE) for path in FONT_PATHS]

# Timing settings
MESSAGE_DISPLAY_TIME = 100  # milliseconds to update text


import subprocess
import json

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

def draw_welcome_message(screen, fonts, welcome_messages, current_message_length):
    """Draw welcome messages on the screen with animation effects."""
    y_positions = [SCREEN_HEIGHT // 4 + i * 100 for i, _ in enumerate(welcome_messages)]

    for i, message in enumerate(welcome_messages):
        reshaped_text = arabic_reshaper.reshape(message[:current_message_length[i]])
        bidi_text = get_display(reshaped_text)
        text_surface = fonts[i].render(bidi_text, True, GREEN)
        alpha_surface = pygame.Surface(text_surface.get_size(), SRCALPHA)
        alpha_surface.fill(WHITE)
        alpha_surface.blit(text_surface, (0, 0), special_flags=BLEND_RGBA_MULT)
        text_rect = alpha_surface.get_rect(center=(SCREEN_WIDTH // 2, y_positions[i]))
        screen.blit(alpha_surface, text_rect)

def fade(alpha):

    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)   
    s.fill((0,0,0,alpha))                     
    screen.blit(s, (0,0))    


def eyes(eyelid_move):
    x = SCREEN_WIDTH // 2
    eyes_space = 200
    y = SCREEN_HEIGHT // 4
    rect_height = SCREEN_HEIGHT // 3
    rect_width = SCREEN_WIDTH // 10

    ## Right Eye
    pygame.draw.rect(screen, GREEN, (x + eyes_space, y , rect_width , rect_height), 0 , 100)
    pygame.draw.rect(screen, BLACK, (x + eyes_space, y , rect_width , eyelid_move))

    ##Left Eye
    pygame.draw.rect(screen, GREEN, (x - eyes_space - rect_width , y , rect_width , rect_height), 0 , 100)
    pygame.draw.rect(screen, BLACK, (x - eyes_space - rect_width, y , rect_width , eyelid_move))

def mouth():
    x = SCREEN_WIDTH // 2
    y = 2*SCREEN_HEIGHT//3 - 100
    radius = 100

    pygame.draw.circle(screen, GREEN, (x,y + radius), radius)
    pygame.draw.rect(screen, BLACK, (x - radius,y + 2 * radius - radius*2, radius*2 , radius+50))




def main():
    finished = False
    not_visited = True
    fade_out = False
    alpha = 0
    clock = pygame.time.Clock()
    current_message_length = [0] * len(WELCOME_MESSAGES)
    last_update_time = pygame.time.get_ticks()
    all_messages_complete = False

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()


        if finished:
             break

        current_time = pygame.time.get_ticks()
        if current_time - last_update_time > MESSAGE_DISPLAY_TIME and not all_messages_complete:
            all_messages_complete = True
            for i in range(len(WELCOME_MESSAGES)):
                if current_message_length[i] < len(WELCOME_MESSAGES[i]):
                    current_message_length[i] += 1
                    all_messages_complete = False  # Ensure we keep updating until all messages are complete
            last_update_time = current_time

        draw_welcome_message(screen, fonts, WELCOME_MESSAGES, current_message_length)

        if all_messages_complete and not_visited:
            pygame.time.wait(60)
            fade_out = True
            not_visited = False

        if fade_out:
            alpha +=2
            if alpha > 255:
                alpha = 254
                finished =True

            fade(alpha)


        pygame.display.flip()

        clock.tick(60)


def processing():
        record('recording')
        message = transcribe('recording')
        thought = convo(message)
        play_text(thought, 'recording')
        os.remove('recording.mp3')

def face(awake, eyelid, command):
    thought = None
    clock = pygame.time.Clock()
    blinking = False
    closing_eyes = False
    blink_speed = 20
    count = 0
    played = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
       

        if not awake:
            record('wake')
            message = transcribe('wake')
            thought = convo(message)
            os.remove('wake.mp3')
            blinking = True
            awake = True

        if blinking and count <= 2:

            if closing_eyes: 

                if eyelid > SCREEN_HEIGHT // 3 + 40:
                    eyelid = SCREEN_HEIGHT // 3 + 40
                    closing_eyes = False
            
                else: 
                    eyelid += blink_speed
            else: 
                
                if eyelid < 0:
                    eyelid = 0
                    closing_eyes = True
                    count += 1
            
                else: 
                    eyelid -= blink_speed

            eyes(eyelid)
        else:
            eyes(eyelid)

        if count >=2 and not played:
            play_text(thought, 'wake')
            played = True
            command = True

        if command:
            record('convo')
            message = transcribe('convo')
            thought = convo(message)
            os.remove('convo.mp3')
            play_text(thought, 'wake')
            pygame.time.wait(1500)
            command = False

        #mouth()

        pygame.display.flip()

        clock.tick(60)

###################################################CODE#######################################################
main()
face(False, SCREEN_HEIGHT // 3, False)


import threading 

def processing_thread():
    try:
        processing()
    except Exception as e:
        print(f"Error in main_thread: {e}")

def face_thread():
    try:
        face(True, 0, True)
    except Exception as e:
        print(f"Error in face_thread: {e}")

def start_threads():
    thread1 = threading.Thread(target=face_thread)
    thread2 = threading.Thread(target=processing_thread)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


start_threads()

