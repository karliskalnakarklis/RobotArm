import pyaudio
import wave

SAMPLE_RATE = 48000  # Match what your hardware supports
DEVICE_INDEX = 0      # Use the actual working index (from that list script!)

p = pyaudio.PyAudio()

stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=SAMPLE_RATE,
    input=True,
    input_device_index=DEVICE_INDEX,
    frames_per_buffer=1024
)

frames = []

print("🎙️ Recording for 5 seconds at 48kHz...")
for _ in range(0, int(SAMPLE_RATE / 1024 * 5)):
    data = stream.read(1024)
    frames.append(data)

print("✅ Done")

stream.stop_stream()
stream.close()
p.terminate()

with wave.open("test_output.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b"".join(frames))

print("🎧 Saved as test_output.wav")
