from vosk import Model, KaldiRecognizer
import pyaudio
import json

model = Model("vosk-model-en-us-0.22")  # path to your downloaded model
rec = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

while True:
    data = stream.read(4000)
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        checktext = result["text"].split(" ")
        for word in checktext:
            if word == "jarvis":
                print("jarvis found")
                result = json.loads(rec.Result())
        print(result["text"])

