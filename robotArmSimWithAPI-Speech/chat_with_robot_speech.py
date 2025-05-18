
import time
from api_chatbox import converse
import wiringpi as wp
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import pyttsx3

# === Servo Setup ===
LR_SERVO_PIN = 2
UD_SERVO_PIN = 3
wp.wiringPiSetup()
wp.softPwmCreate(LR_SERVO_PIN, 0, 200)
wp.softPwmCreate(UD_SERVO_PIN, 0, 200)

def set_angle(pin, angle):
    pulse = int(5 + (angle / 180.0) * 20)
    wp.softPwmWrite(pin, pulse)

def nod(duration=3):
    end_time = time.time() + duration
    while time.time() < end_time:
        for a in (90, 150, 90, 30, 90):
            set_angle(UD_SERVO_PIN, a)
            time.sleep(0.2)

def shake(duration=3):
    end_time = time.time() + duration
    while time.time() < end_time:
        for a in (90, 150, 90, 30, 90):
            set_angle(LR_SERVO_PIN, a)
            time.sleep(0.2)

def wait_motion(duration=3):
    end_time = time.time() + duration
    while time.time() < end_time:
        set_angle(LR_SERVO_PIN, 70)
        set_angle(UD_SERVO_PIN, 110)
        time.sleep(0.2)
        set_angle(LR_SERVO_PIN, 110)
        set_angle(UD_SERVO_PIN, 70)
        time.sleep(0.2)

# === TTS Setup ===
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
if len(voices) > 1:
    engine.setProperty('voice', voices[0].id)

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# === Vosk Setup ===
model = Model("vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                input=True, frames_per_buffer=8000)
stream.start_stream()

print("🎙️ Say 'Jarvis' followed by your command...")

conv_id = None

while True:
    data = stream.read(4000, exception_on_overflow=False)
    if rec.AcceptWaveform(data):
        result_json = json.loads(rec.Result())
        spoken_text = result_json.get("text", "").lower()

        if not spoken_text or "jarvis" not in spoken_text:
            continue

        print(f"🧏 Heard: {spoken_text}")
        command = spoken_text.split("jarvis", 1)[-1].strip()
        if not command:
            print("🤔 Detected 'Jarvis' but no command.")
            continue

        wait_motion()

        try:
            result = converse(command, conversation_id=conv_id)
            conv_id = result.get("conversation_id", conv_id)
            reply = result.get("speech", {}).get("plain", {}).get("speech", "<no reply>")
            print(f"🤖 Assistant: {reply}")
            speak_text(reply)
            nod()
        except Exception as e:
            print("⚠️ Error communicating with assistant:", e)
            shake()
