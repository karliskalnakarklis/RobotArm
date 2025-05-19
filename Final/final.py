import subprocess
import requests
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import numpy as np
import queue

# === 🔊 TTS Setup (eSpeak-NG) ===
def speak(text):
    try:
        # Using better quality settings for eSpeak-NG
        subprocess.run(['espeak-ng', '-v', 'en-us', '-s', '150', text])
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

# Audio configuration
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 4000
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """This is called for each audio block from the microphone."""
    if status:
        print(status, flush=True)
    audio_queue.put(bytes(indata))

# === Main Program ===
try:
    # List available audio devices
    print("Available audio devices:")
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        print(f"{i}: {dev['name']} (Input channels: {dev['max_input_channels']})")

    # Find suitable input device
    input_device = None
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            input_device = i
            print(f"Selected input device: {dev['name']}")
            break

    if input_device is None:
        raise RuntimeError("No suitable input device found")

    # Start audio stream
    with sd.InputStream(device=input_device,
                       channels=CHANNELS,
                       samplerate=SAMPLE_RATE,
                       callback=audio_callback,
                       blocksize=BLOCK_SIZE,
                       dtype='int16'):
        print("🗣️ Listening for 'Jarvis'...")
        conv_id = None

        while True:
            try:
                # Get audio data from queue
                data = audio_queue.get()
                
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

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"⚠️ Error: {e}")
                continue

except Exception as e:
    print(f"Fatal error: {e}")