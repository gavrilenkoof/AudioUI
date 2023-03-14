import logging
import pyaudio
import numpy as np
import scipy.signal as sps


logger = logging.getLogger(__name__.replace('__', ''))



class Converter:

    def __init__(self, need_convert, target_sample_rate):
        super(Converter, self).__init__()
        self._need_convert = need_convert
        # self._mic_source_sample_rate = source_sample_rate
        self._target_sample_rate = target_sample_rate
        # self.form = format


    def convert_mic(self):
        pass

    def covert_file_audio(self):
        pass

    
    @staticmethod
    def map_int(self, x, in_min=0, in_max=255, out_min=-32768, out_max=32767):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    @staticmethod
    def db_to_float(headroom=0.1):
        return 10 ** (headroom / 20)
    
    @staticmethod
    def normalize(data, max_val_input, max_range_val):
        return (data / max_val_input) * max_range_val 
    
    def _converting_file(self, data, source_sample_rate):
        
        if len(data.shape) >= 2:
            data = data.reshape((data.shape[0] * data.shape[1], 1))
            data = np.delete(data, np.arange(1, data.shape[0], 2))

        if data.dtype == np.uint8:
            logger.warning("Convert from uint8 to int16 format")
            data = data.astype(np.int16)
            data = Converter.map_int(data)

        logger.debug(f"source sample rate: {source_sample_rate}")
        number_of_samples = round(len(data) * self._target_sample_rate / source_sample_rate)
        data = sps.resample(data, number_of_samples, window="triang")
        logger.debug(f"new sample rate: {self._target_sample_rate}")

        max_val = np.max(np.abs(data))
        if max_val != 0:
            target_max_val = (32767 * Converter.db_to_float(-1.0))
            data = Converter.normalize(data, max_val, target_max_val)


        return data


    def prepare_wav_file(self, data, source_sample_rate):

        new_data = data

        if self._need_convert is True:
            logger.info("Prepare wav file")
            new_data = self._converting_file(data, source_sample_rate)

        return new_data

    def get_target_sample_rate(self):
        return self._target_sample_rate