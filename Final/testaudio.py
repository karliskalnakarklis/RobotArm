import pyaudio
import wave

p = pyaudio.PyAudio()

stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    input_device_index=0,
    frames_per_buffer=1024
)

frames = []

print("🎙️ Recording for 5 seconds...")
for _ in range(0, int(16000 / 1024 * 5)):
    data = stream.read(1024)
    frames.append(data)

print("✅ Done")

stream.stop_stream()
stream.close()
p.terminate()

with wave.open("test_output.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b"".join(frames))

print("🎧 Saved as test_output.wav")
