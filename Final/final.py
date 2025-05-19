import subprocess
import requests
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import time
import numpy as np

# === 🔊 TTS Setup ===
def speak(text):
    try:
        subprocess.run(['espeak-ng', '-v', 'en-us+m3', '-s', '150', text])
    except Exception as e:
        print("TTS Error:", e)

# === Audio Configuration ===
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 8000  # Increased buffer size
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

# === Vosk Speech Recognition ===
def init_vosk():
    model = Model("vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)  # Enable word-level timings
    rec.SetPartialWords(True)  # Enable partial results
    return rec

# === Main Program ===
def main():
    # Initialize recognizer
    rec = init_vosk()
    
    # Audio device setup
    input_device = None
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0 and 'ac200' in dev['name'].lower():
            input_device = i
            break
    
    if input_device is None:
        input_device = sd.default.device[0]
    
    print(f"\nUsing audio device: {devices[input_device]['name']}")
    print("Listening... (Say 'Jarvis' followed by your command)")

    with sd.InputStream(device=input_device,
                      channels=CHANNELS,
                      samplerate=SAMPLE_RATE,
                      callback=audio_callback,
                      blocksize=BLOCK_SIZE,
                      dtype='int16'):
        
        conv_id = None
        silence_threshold = 0.02  # Adjust based on your environment
        last_speech_time = time.time()

        while True:
            try:
                if not audio_queue.empty():
                    data = audio_queue.get()
                    
                    # Check audio energy level
                    audio_energy = np.sqrt(np.mean(data**2))
                    if audio_energy < silence_threshold:
                        continue
                    
                    # Process with Vosk
                    if rec.AcceptWaveform(data.tobytes()):
                        result = json.loads(rec.Result())
                        text = result.get('text', '').lower()
                        if text and "jarvis" in text:
                            command = text.split('jarvis', 1)[1].strip()
                            if command:
                                print(f"\nCommand: {command}")
                                reply, conv_id = converse(command, conv_id)
                                print(f"Assistant: {reply}")
                                speak(reply)
                    else:
                        # Get partial results for debugging
                        partial = json.loads(rec.PartialResult())
                        if 'partial' in partial:
                            print(f"\rListening: {partial['partial']}", end='')
                    
                    last_speech_time = time.time()
                
                # Visual feedback
                if time.time() - last_speech_time > 3:
                    print("\rWaiting for speech...", end='')
                
                time.sleep(0.05)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                continue

if __name__ == "__main__":
    main()