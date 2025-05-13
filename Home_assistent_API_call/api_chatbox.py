import requests
import uuid
from vosk import Model, KaldiRecognizer
import pyaudio
import json

# === 🔧 Home Assistant Config ===
HA_URL = "https://tfd9eaklrsaswbraeoswnlyfx4pmaaoj.ui.nabu.casa"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjYzIxZDIyZDdjZmE0MGQ1YTIxMjYyOWMwNDIyNzJlYSIsImlhdCI6MTc0NjcwNTMyMSwiZXhwIjoyMDYyMDY1MzIxfQ.UI0lzY2hLPEFmWQaHkvjw-VGwLzie_-PXNA2PMIPvws"  # ⚠️ KEEP THIS SECRET
AGENT_ID = "conversation.llama3_2_2"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}
ENDPOINT = "/api/conversation/process"

# === 🧠 Function to talk to HA ===
def converse(text: str, conversation_id: str = None) -> dict:
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
    return response.json()

# === 🎙️ Voice Input Setup ===
model = Model("vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                input=True, frames_per_buffer=8000)
stream.start_stream()

print("🗣️ Listening for 'Jarvis'...")

conv_id = None  # To keep conversation context

while True:
    data = stream.read(4000, exception_on_overflow=False)
    if rec.AcceptWaveform(data):
        result_json = json.loads(rec.Result())
        spoken_text = result_json.get("text", "")
        if not spoken_text:
            continue

        print(f"🧏 Heard: {spoken_text}")

        # Check for wake word
        if "jarvis" in spoken_text:
            print("🚨 Wake word detected: 'Jarvis'")

            # Extract what's said after 'jarvis'
            split_text = spoken_text.split("jarvis", 1)
            command = split_text[1].strip() if len(split_text) > 1 else ""

            if command == "":
                print("🤔 You said 'Jarvis' but gave no command.")
                continue

            try:
                # Send to Home Assistant
                result = converse(command, conversation_id=conv_id)
                conv_id = result.get("conversation_id", conv_id)
                reply = result.get("response") or result.get("result") or "<no response>"
                print(f"🤖 Assistant: {reply}")
            except Exception as e:
                print(f"⚠️ Error talking to Home Assistant: {e}")
