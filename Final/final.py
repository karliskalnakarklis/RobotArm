import subprocess
import requests
import json
from vosk import Model, KaldiRecognizer
import pyaudio

# === 🔊 TTS Setup (eSpeak-NG) ===
def speak(text):
    try:
        # Basic eSpeak-NG usage
        subprocess.run(['espeak-ng', '-v', 'en-us', text])
        
        # For better quality (slower):
        # subprocess.run(['espeak-ng', '-v', 'en-us', '-s', '150', '-p', '50', text])
    except Exception as e:
        print("Error during TTS:", e)

# === 🧠 Home Assistant Setup ===
HA_URL = "https://tfd9eaklrsaswbraeoswnlyfx4pmaaoj.ui.nabu.casa"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjYzIxZDIyZDdjZmE0MGQ1YTIxMjYyOWMwNDIyNzJlYSIsImlhdCI6MTc0NjcwNTMyMSwiZXhwIjoyMDYyMDY1MzIxfQ.UI0lzY2hLPEFmWQaHkvjw-VGwLzie_-PXNA2PMIPvws"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}
ENDPOINT = "/api/conversation/process"

def converse(text: str, conversation_id: str = None):
    url = f"{HA_URL}{ENDPOINT}"
    payload = {
        "text": text,
        "agent_id": "conversation.llama3_2_2",
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get("response") or data.get("result") or "<no response>", data.get("conversation_id")

# === 🎤 Vosk Setup ===
model = Model("vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=0,  # ← or 2 / 3 depending on what works!
                frames_per_buffer=8000)
stream.start_stream()

print("🗣️ Listening for 'Jarvis'...")
conv_id = None

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
            command = spoken_text.split("jarvis", 1)[1].strip() if len(spoken_text.split("jarvis", 1)) > 1 else ""

            if not command:
                print("🤔 You said 'Jarvis' but gave no command.")
                continue

            try:
                reply, conv_id = converse(command, conversation_id=conv_id)
                print(f"🤖 Assistant: {reply}")
                speak(reply)
            except Exception as e:
                print(f"⚠️ Error talking to Home Assistant: {e}")