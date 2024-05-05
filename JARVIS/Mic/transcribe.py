from openai import OpenAI
import json 

def transcribe():
    client = OpenAI(api_key='') #input ur api key here
    file= open("recording.mp3", "rb")
    translation = client.audio.translations.create(
    model="whisper-1", 
    file=file
    )
    return translation.text



response_data = {"message": transcribe()}

# Send response to stdout
print(json.dumps(response_data))
