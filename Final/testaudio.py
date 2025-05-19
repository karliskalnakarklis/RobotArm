import pyaudio

p = pyaudio.PyAudio()

# List available devices
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"ID {i}: {info['name']} - Channels: {info['maxInputChannels']}")

# Test recording from device 0
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                input=True,
                input_device_index=2,  # Your selected mic device
                frames_per_buffer=1024)

print("Recording...")

try:
    while True:
        data = stream.read(1024)
        volume = max(data)
        print(f"Volume: {volume}")
except KeyboardInterrupt:
    print("Stopping...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
