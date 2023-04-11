from opuslib import Encoder, Decoder

from log import get_logger

logger = get_logger(__name__.replace('__', ''))




class OpusCodec:

    def __init__(self, sample_rate, channels, mode="audio"):

        self._sample_rate = sample_rate
        self._channels = channels
        self._mode = mode

        self._encoder = Encoder(self._sample_rate, self._channels, self._mode)
        self._decoder = Decoder(self._sample_rate, self._channels)