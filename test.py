import pyaudio
import wave
import audioop
 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "file.wav"
 
audio = pyaudio.PyAudio()
 
# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)



print(audio.get_default_input_device_info())


print("recording...")
frames = []
cvstate = None

def mapIntToInt(x, inp_min=0, inp_max=65535, out_min=0, out_max=255):
    return (x - inp_min) * (out_max - out_min) / (inp_max - inp_min) + out_min
    

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    new_data, cvstate = audioop.ratecv(data, 2, 1, 44100, 16000, cvstate)

    new_data = audioop.lin2lin(new_data, 2, 1)
    new_data = audioop.bias(new_data, 1, 128)

    frames.append(new_data)

print("finished recording")
 
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

val = audio.get_sample_size(FORMAT)
 
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(1)
waveFile.setframerate(16000)
waveFile.writeframes(b''.join(frames))
waveFile.close()