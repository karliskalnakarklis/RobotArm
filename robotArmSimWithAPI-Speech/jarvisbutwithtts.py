import pyttsx3
import requests
import uuid
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import re

# === 🔊 TTS Setup ===
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# Get female voice if available
voices = engine.getProperty('voices')
if len(voices) > 1:
    engine.setProperty('voice', voices[0].id)

def speak(response):
    try:
        # Extract actual speech text
        text = response['speech']['plain']['speech']
        if not isinstance(text, str):
            raise TypeError("Speech value is not a string.")

        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("Error during TTS:", e)


# === 🧠 Home Assistant Setup ===
HA_URL = "https://tfd9eaklrsaswbraeoswnlyfx4pmaaoj.ui.nabu.casa"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjYzIxZDIyZDdjZmE0MGQ1YTIxMjYyOWMwNDIyNzJlYSIsImlhdCI6MTc0NjcwNTMyMSwiZXhwIjoyMDYyMDY1MzIxfQ.UI0lzY2hLPEFmWQaHkvjw-VGwLzie_-PXNA2PMIPvws"  # ⚠️ Be sure to keep this safe
AGENT_ID = "conversation.llama3_2_2"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}
ENDPOINT = "/api/conversation/process"

def converse(text: str, conversation_id: str = None) -> str:
    url = f"{HA_URL}{ENDPOINT}"
    payload = {
        "text": text,
        "agent_id": AGENT_ID,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    print(f"\n➡️ Talking to Home Assistant...")
    print("📝 Text:", text)

    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()

    # Return the actual response string (not the full JSON)
    return data.get("response") or data.get("result") or "<no response>", data.get("conversation_id")

# === 🎤 Vosk Setup ===
model = Model("vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                input=True, frames_per_buffer=8000)
stream.start_stream()

print("🗣️ Listening for 'Jarvis'...")

conv_id = None  # Keep conversation context

while True:
    data = stream.read(4000, exception_on_overflow=False)
    if rec.AcceptWaveform(data):
        result_json = json.loads(rec.Result())
        spoken_text = result_json.get("text", "").lower()
        if not spoken_text:
            continue

        print(f"🧏 Heard: {spoken_text}")

        if "jarvis" in spoken_text:
            print("🚨 Wake word detected: 'Jarvis'")
            split_text = spoken_text.split("jarvis", 1)
            command = split_text[1].strip() if len(split_text) > 1 else ""

            if command == "":
                print("🤔 You said 'Jarvis' but gave no command.")
                continue

            try:
                reply, conv_id = converse(command, conversation_id=conv_id)
                print(f"🤖 Assistant: {reply}")
                speak(reply)  # Speak only the reply
            except Exception as e:
                print(f"⚠️ Error talking to Home Assistant: {e}")
