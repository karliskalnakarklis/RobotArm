import pyttsx3
import requests
import uuid
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import librosa
import numpy as np
import subprocess

# ===== 🔊 Audio Configuration =====
SAMPLE_RATE_HW = 48000       # Mic's hardware-supported rate
SAMPLE_RATE_VOSK = 16000     # Vosk's required rate

# ===== 🎤 Resampling Function =====
def resample_audio(audio_data_48k):
    """Resample raw 48kHz audio to 16kHz using librosa."""
    audio_np = np.frombuffer(audio_data_48k, dtype=np.int16)
    audio_resampled = librosa.resample(
        audio_np.astype(np.float32), 
        orig_sr=SAMPLE_RATE_HW, 
        target_sr=SAMPLE_RATE_VOSK
    )
    return audio_resampled.astype(np.int16).tobytes()

# ===== 🗣️ TTS Setup (espeak) =====
def speak(response):
    """Extracts plain speech from HA response and uses espeak to speak it."""
    try:
        # Get the speech string from the response dictionary
        text = response.get("speech", {}).get("plain", {}).get("speech", "")
        if not text or not isinstance(text, str):
            print("⚠️ No valid speech string found in response.")
            return

        print(f"🗣️ Speaking: {text}")
        subprocess.run(['espeak', '-s150', text])
    except Exception as e:
        print("🚨 Error during TTS:", e)


# ===== 🧠 Home Assistant Setup =====
HA_URL = "https://tfd9eaklrsaswbraeoswnlyfx4pmaaoj.ui.nabu.casa"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjYzIxZDIyZDdjZmE0MGQ1YTIxMjYyOWMwNDIyNzJlYSIsImlhdCI6MTc0NjcwNTMyMSwiZXhwIjoyMDYyMDY1MzIxfQ.UI0lzY2hLPEFmWQaHkvjw-VGwLzie_-PXNA2PMIPvws" 
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def converse(text, conversation_id=None):
    """Send user text to Home Assistant's LLM agent."""
    payload = {
        "text": text,
        "agent_id": "conversation.llama3_2_2"
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    print(f"📡 Sending to Home Assistant: {text}")
    response = requests.post(f"{HA_URL}/api/conversation/process", headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "<no response>"), data.get("conversation_id")

# ===== 🎧 Vosk Setup =====
model = Model("vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, SAMPLE_RATE_VOSK)

p = pyaudio.PyAudio()

# List available audio devices
print("Available audio devices:")
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print(f"{i}: {dev['name']} (Input channels: {dev['maxInputChannels']})")

# Use USB microphone (card 2, device 0 from your aplay -l output)
# You may need to adjust this index based on the printed list
USB_MIC_INDEX = None
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if "G432" in dev['name'] and dev['maxInputChannels'] > 0:
        USB_MIC_INDEX = i
        break

if USB_MIC_INDEX is None:
    print("⚠️ No suitable USB microphone found. Using default input device.")
    USB_MIC_INDEX = p.get_default_input_device_info()['index']

print(f"Using audio device index: {USB_MIC_INDEX}")

stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=SAMPLE_RATE_HW,
    input=True,
    input_device_index=USB_MIC_INDEX,
    frames_per_buffer=2048
)

# ===== 🤖 Main Loop =====
print("🧠 Listening for 'Jarvis' at 48kHz (resampled to 16kHz)...")
conv_id = None

try:
    while True:
        data_48k = stream.read(2048, exception_on_overflow=False)
        data_16k = resample_audio(data_48k)

        if rec.AcceptWaveform(data_16k):
            result = json.loads(rec.Result())
            spoken = result.get("text", "").lower()
            if not spoken:
                continue

            print(f"🧏 Heard: {spoken}")

            if "jarvis" in spoken:
                print("🚨 Wake word detected!")
                command = spoken.split("jarvis", 1)[1].strip()
                if not command:
                    print("🤷 You said 'Jarvis' but nothing after that.")
                    continue

                reply, conv_id = converse(command, conversation_id=conv_id)
                print(f"🤖 Assistant: {reply}")
                speak(reply)

except KeyboardInterrupt:
    print("\n👋 Shutting down like a polite robot...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
