from pathlib import Path
from openai import OpenAI
from playsound import playsound
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


def play_text(client, message):
  speech_file_path = Path(__file__).parent / "speech.mp3"
  response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=message
)
  response.stream_to_file(speech_file_path)

  playsound(speech_file_path)

