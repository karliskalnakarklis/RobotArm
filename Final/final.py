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
SAMPLE_RATE_HW = 48000  # Hardware-supported rate (from arecord test)
SAMPLE_RATE_VOSK = 16000  # Vosk's preferred rate

# ===== 🎤 Audio Resampling Function =====
def resample_audio(audio_data_48k):
    """Resamples 48kHz audio to 16kHz for Vosk"""
    audio_np = np.frombuffer(audio_data_48k, dtype=np.int16)
    audio_resampled = librosa.resample(
        audio_np.astype(np.float32),
        orig_sr=SAMPLE_RATE_HW,
        target_sr=SAMPLE_RATE_VOSK
    )
    return audio_resampled.astype(np.int16).tobytes()

# ===== 🔊 TTS Setup (Lightweight ESpeak) =====
def speak(text):
    """Uses espeak for better Pi compatibility"""
    subprocess.run(['espeak', '-s150', text])

# ===== 🧠 Home Assistant Setup =====
HA_URL = "https://your-ha-url.com"
TOKEN = "your-long-lived-token"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def converse(text, conversation_id=None):
    payload = {
        "text": text,
        "agent_id": "conversation.llama3_2_2"
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    response = requests.post(
        f"{HA_URL}/api/conversation/process",
        headers=HEADERS,
        json=payload
    )
    data = response.json()
    return data.get("response", "<no response>"), data.get("conversation_id")

# ===== 🎤 Vosk Setup =====
model = Model("vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, SAMPLE_RATE_VOSK)

# ===== 🎤 PyAudio Setup (48kHz Hardware) =====
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=SAMPLE_RATE_HW,  # Matches hardware capability
    input=True,
    input_device_index=0,  # Use hw:0,0
    frames_per_buffer=2048  # Smaller = less latency, higher CPU
)

# ===== 🤖 Main Loop =====
print("🗣️ Listening for 'Jarvis' at 48kHz (resampling to 16kHz for Vosk)...")
conv_id = None

try:
    while True:
        # Read 48kHz audio from hardware
        data_48k = stream.read(2048, exception_on_overflow=False)
        
        # Resample to 16kHz for Vosk
        data_16k = resample_audio(data_48k)
        
        if rec.AcceptWaveform(data_16k):
            result = json.loads(rec.Result())
            text = result.get("text", "").lower()
            
            if "jarvis" in text:
                command = text.split("jarvis", 1)[1].strip()
                if command:
                    print(f"🎤 Heard command: {command}")
                    reply, conv_id = converse(command, conv_id)
                    print(f"🤖 Assistant: {reply}")
                    speak(reply)

except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()