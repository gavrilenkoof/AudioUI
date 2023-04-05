import pyaudio
import numpy as np
import scipy.signal as sps

from log import get_logger

logger = get_logger(__name__.replace('__', ''))




class Converter:

    def __init__(self, need_convert, target_sample_rate):
        super(Converter, self).__init__()
        self._need_convert = need_convert
        self._target_sample_rate = target_sample_rate


    def convert_mic(self, message, source_sample_rate):

        number_of_samples = round(len(message) * self.get_target_sample_rate() / source_sample_rate)
        message = sps.resample(message, number_of_samples, window="bohman")

        return message
        

    def covert_file_audio(self):
        pass

    
    @staticmethod
    def map_int(x, in_min=0, in_max=255, out_min=-32768, out_max=32767):
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
            data = data.astype(np.int16)
            data = Converter.map_int(data)




        number_of_samples = round(len(data) * self._target_sample_rate / source_sample_rate)
        # data = sps.resample(data, number_of_samples, window=("dpss", 0.5))
        data = sps.resample(data, number_of_samples, window="bohman")
        # data = sps.resample(data, number_of_samples, window="blackman")

        # max_val = 32000
        # if max_val != 0:
        #     target_max_val = (32767 * Converter.db_to_float(-0.1))
        #     data = Converter.normalize(data, max_val, target_max_val)


        # data = self._butter_highpass_filter(data, 50, self._target_sample_rate)
        # data = self._butter_lowpass_filter(data, 7999, self._target_sample_rate, 5)

        return data
    

    def _butter_highpass(self, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = sps.butter(order, normal_cutoff, btype='high', analog=False)
        return b, a

    def _butter_highpass_filter(self, data, cutoff, fs, order=5):
        b, a = self._butter_highpass(cutoff, fs, order=order)
        y = sps.filtfilt(b, a, data)
        return y
    
    def _butter_lowpass(self, cutoff, fs, order=5):
        return sps.butter(order, cutoff, fs=fs, btype='low', analog=False)

    def _butter_lowpass_filter(self, data, cutoff, fs, order=5):
        b, a = self._butter_lowpass(cutoff, fs, order=order)
        y = sps.lfilter(b, a, data)
        return y



    def convert_file(self, data, source_sample_rate):
        new_data = data
        if self._need_convert is True:
            new_data = self._converting_file(data, source_sample_rate)

        return new_data

    def get_target_sample_rate(self):
        return self._target_sample_rate