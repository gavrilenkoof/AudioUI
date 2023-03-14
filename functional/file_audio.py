import logging
from scipy.io import wavfile


logger = logging.getLogger(__name__.replace('__', ''))



class FileAudio:

    def __init__(self):
        super(FileAudio, self).__init__()
        self._data = None
        self._number_frame = 0
        self._source_sample_rate = 0

        self._prepared_all_data = None

    def open(self, file_name_url):
        self._file_name_url = file_name_url

    def close(self):
        self._data = None
        self._prepared_all_data = None
        self._number_frame = 0

    def read_all(self):

        self._number_frame = 0
        self._source_sample_rate, self._data = wavfile.read(self._file_name_url)
        return self._data, self._source_sample_rate

    def read(self, chunk):
        pass

    def get_next_chunk_data(self, chunk):
        data = self._prepared_all_data[self._number_frame * chunk: (self._number_frame + 1) * chunk]

        if self._number_frame >= int(len(self._prepared_all_data) / chunk):
            self._number_frame = 0
        else:
            self._number_frame += 1

        return data

    def set_prepared_all_data(self, data):
        self._prepared_all_data = data
