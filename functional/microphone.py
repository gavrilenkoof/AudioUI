import pyaudio


from log import get_logger

logger = get_logger(__name__.replace('__', ''))


class Microphone:

    
    def __init__(self, channel, format):
        super(Microphone, self).__init__()

        self._audio = pyaudio.PyAudio()
        self._source_sample_rate = int(self._audio.get_default_input_device_info()["defaultSampleRate"])
        self._channel = channel
        self._format = format        

        self._stream = None
        self._in_use = False

        self._is_connect = False

    def get_source_sample_rate(self):
        return self._source_sample_rate
    
    def get_status_connect(self) -> bool:
        return self._is_connect
    
    def enable(self):
        self._is_connect = True
        self._stream = self._audio.open(format=self._format, rate=self._source_sample_rate,
                                        channels=self._channel, input=True,
                                        start=True)
        
    def disable(self):
        self._is_connect = False
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