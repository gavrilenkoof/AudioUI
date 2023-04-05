from scipy.io import wavfile

from functional.wav_audio import WavAudio


from log import get_logger

logger = get_logger(__name__.replace('__', ''))



class FileAudio:

    def __init__(self):
        super(FileAudio, self).__init__()

        self._is_file_open = False

        self._wav_file_handler = WavAudio()

    def get_status_file(self) -> bool:
        return self._is_file_open

    def get_source_sample_rate(self):
        return self._wav_file_handler.get_source_sample_rate()

    
    def is_file_end(self):
        return self._wav_file_handler.is_file_end()
    
    def restart_file(self):
        self._wav_file_handler.restart_file()


    def open(self, file_name_url):
        self._is_file_open = True
        self._file_name_url = file_name_url

        logger.info("Open WAV File")

        self._wav_file_handler.open_file(self._file_name_url)

    def close(self):
        self._is_file_open = False

        logger.info("Close WAV File")
        try:
            self._wav_file_handler.close_file()
        except AttributeError as ex:
            logger.info(f"NoneType obj: {ex}")


    def read(self, chunk):
        data = None

        data = self._wav_file_handler.read_data(chunk)

        return data


