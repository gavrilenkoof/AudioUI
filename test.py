import pyaudio
import wave
import audioop
 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1
RECORD_SECONDS = 5

CHUNK_AUDIO = int(1024 / (44100 / 16000)) + 1

WAVE_OUTPUT_FILENAME = "file.wav"
 
audio = pyaudio.PyAudio()
 
# start Recording mic
stream_input = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)


stream_output = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=16000, output=True,
                    frames_per_buffer=CHUNK_AUDIO)


print("recording...")
frames = []
cvstate = None

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream_input.read(CHUNK)
    new_data, cvstate = audioop.ratecv(data, 2, 1, 44100, 16000, cvstate)
    new_data = audioop.lin2lin(new_data, 2, 1)
    new_data = audioop.bias(new_data, 1, 128)

    # frames.append(new_data)
    stream_output.write(data)

print("finished recording")
 
# stop Recording
stream_input.stop_stream()
stream_input.close()
audio.terminate()

stream_output.stop_stream()
stream_output.close()

val = audio.get_sample_size(FORMAT)
 
# waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# waveFile.setnchannels(CHANNELS)
# waveFile.setsampwidth(1)
# waveFile.setframerate(16000)
# waveFile.writeframes(b''.join(frames))
# waveFile.close()

waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(2)
waveFile.setframerate(44100)
waveFile.writeframes(b''.join(frames))
waveFile.close()