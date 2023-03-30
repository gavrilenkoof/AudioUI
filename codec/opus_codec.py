from pyogg import OpusEncoder
from pyogg import OpusDecoder

class OpusCodec:
    


    def __init__(self):
        self.opus_encoder = OpusEncoder()
        self.opus_decoder = OpusDecoder()


    def encode(self, data):
            # We haven't read a full frame from the wav file, so this
            # is most likely a final partial frame before the end of
            # the file.  We'll pad the end of this frame with silence.
        encoded_packet = self.opus_encoder.encode(data)
        return  encoded_packet
    def encoder_create(self,application, sample_rate, channels):
        self.opus_encoder.set_application(application)
        self.opus_encoder.set_sampling_frequency(sample_rate)
        self.opus_encoder.set_channels(channels)
        return 0
        
    def decode(self):
        return "hello"