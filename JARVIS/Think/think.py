from openai import OpenAI
import sys
import json 
from pathlib import Path


client = OpenAI(api_key='') #input ur API key here
input_data = sys.stdin.read()
data = json.loads(input_data)

def think(message):
  stream = client.chat.completions.create(
      model="gpt-4",
      messages=[{"role": "system", "content": message}],
      stream=False,
  )
  return stream.choices[0].message.content

thought = think(data['message'])

response_data = {"message": thought, "state":True}

# Send response to stdout
print(json.dumps(response_data))



