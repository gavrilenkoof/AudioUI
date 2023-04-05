from scipy.io import wavfile

from functional.wav_audio import WavAudio


from log import get_logger

logger = get_logger(__name__.replace('__', ''))



class FileAudio:

    def __init__(self):
        super(FileAudio, self).__init__()
        self._data = None
        self._number_frame = 0
        self._source_sample_rate = 0

        self._prepared_all_data = None

        self._is_file_open = False

        self._ready_for_use_prepared_data = False

        self._wav_file_handler = WavAudio()

    def get_status_file(self) -> bool:
        return self._is_file_open
    
    def get_ready_upload_all_data(self) -> bool:
        return self._ready_for_use_prepared_data
    
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
        self._data = None
        self._prepared_all_data = None
        self._number_frame = 0

        logger.info("Close WAV File")
        try:
            self._wav_file_handler.close_file()
        except AttributeError as ex:
            logger.info(f"NoneType obj: {ex}")

    def read_all(self):
        self._ready_for_use_prepared_data = False
        self._number_frame = 0
        self._source_sample_rate, self._data = wavfile.read(self._file_name_url)
        return self._data, self._source_sample_rate

    def read(self, chunk):
        data = None

        self._source_sample_rate, data = self._wav_file_handler.read_data(chunk)

        return self._source_sample_rate, data

    def get_next_chunk_data(self, chunk):
        data = self._prepared_all_data[self._number_frame * chunk: (self._number_frame + 1) * chunk]

        if self._number_frame >= int(len(self._prepared_all_data) / chunk):
            self._number_frame = 0
        else:
            self._number_frame += 1
        return data

    def set_prepared_all_data(self, data):
        self._ready_for_use_prepared_data = True
        self._prepared_all_data = data
