import subprocess
import requests
import json
import os
from vosk import Model, KaldiRecognizer
import pyaudio
import time

# === 🔊 TTS Setup ===
def speak(text):
    try:
        subprocess.run(['espeak-ng', '-v', 'en-us+m3', '-s', '150', text])
    except Exception as e:
        print("TTS Error:", e)

# === Audio Configuration ===
def setup_audio():
    p = pyaudio.PyAudio()
    
    # List available devices
    print("\nAvailable audio devices:")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print(f"{i}: {dev['name']} (Input channels: {dev['maxInputChannels']})")
    
    # Try to find the correct device
    input_device = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0 and 'ac200' in dev['name'].lower():
            input_device = i
            break
    
    if input_device is None:
        print("Warning: Using default input device")
        input_device = p.get_default_input_device_info()['index']
    
    print(f"\nUsing device: {input_device} - {p.get_device_info_by_index(input_device)['name']}")
    
    # Configure stream with explicit device settings
    stream = p.open(format=pyaudio.paInt16,
                   channels=1,
                   rate=16000,
                   input=True,
                   input_device_index=input_device,
                   frames_per_buffer=8000)
    return p, stream

# === Main Program ===
def main():
    # Initialize Vosk
    model = Model("vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, 16000)
    
    # Setup audio
    p, stream = setup_audio()
    
    print("\nListening for 'Jarvis'... (Press Ctrl+C to stop)")
    
    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get('text', '').lower()
                if text and "jarvis" in text:
                    command = text.split('jarvis', 1)[1].strip()
                    if command:
                        print(f"\nCommand: {command}")
                        # Add your Home Assistant integration here
                        response = "I heard: " + command
                        print("Assistant:", response)
                        speak(response)
            else:
                # Show we're listening
                print(".", end="", flush=True)
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    # First verify ALSA configuration
    print("Verifying ALSA configuration...")
    os.system('alsamixer')  # Check this shows your audio device
    os.system('arecord -l')  # Should list your microphone
    
    # Run main program
    main()