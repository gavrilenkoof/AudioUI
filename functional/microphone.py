import pyaudio
import logging


logger = logging.getLogger(__name__.replace('__', ''))


class Microphone:

    MSG_LEN_BYTES = 512
    
    def __init__(self, channel, format):
        super(Microphone, self).__init__()

        self._audio = pyaudio.PyAudio()
        self._source_sample_rate = int(self._audio.get_default_input_device_info()["defaultSampleRate"])
        self._channel = channel
        self._format = format        

        self._stream = None
        self._in_use = False

    def get_source_sample_rate(self):
        return self._source_sample_rate
    
    def enable(self):
        self._stream = self._audio.open(format=self._format, rate=self._source_sample_rate,
                                        channels=self._channel, input=True,
                                        start=True)
        
    def disable(self):
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()

    def close(self):
        self.disable()
        self._audio.terminate()

    def read(self, chunk):

        data = None

        try:
            self._in_use = True
            data = self._stream.read(chunk)

        except AttributeError as ex:
            logger.error(f"AttributeError MIC. {ex}")
        except OSError as ex:
            logger.error(f"OSError MIC. {ex}")
        finally:
            self._in_use = False
        
        return data
    

    def is_active(self):
        return self._stream.is_active()