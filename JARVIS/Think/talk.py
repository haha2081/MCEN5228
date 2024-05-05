from openai import OpenAI
import sys
import json 
from pathlib import Path
from playsound import playsound

client = OpenAI(api_key='') #input ur API key here

input_data = sys.stdin.read()
data = json.loads(input_data)


def play_text(client, message):
  speech_file_path = Path(__file__).parent / "speech.mp3"
  response = client.audio.speech.create(
    model="tts-1",
    voice="fable",
    input=message
)
  response.stream_to_file(speech_file_path)

  playsound(speech_file_path)

play_text(client, data['message'])

response_data = {"state":True}

# Send response to stdout
print(json.dumps(response_data))





