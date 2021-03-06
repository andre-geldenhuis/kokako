"""A detector for Hihi. This is just a specific version of
TFGraphDetector with some hardcoded parameters to point to a pre-trained
Hihi detector."""
import os
import numpy as np

from kokako.detectors.tfgraph import TFGraphUser
from kokako.score import Detector


class HihiCNN(Detector, TFGraphUser):
    code = 'hihi'
    description = 'Loads a trained convolutional neural net for Hihi detection'
    version = '0.0.1'

    def __init__(self, detector_path=None, prediction_block_size=10, num_cores=None):
        """Loads a hihi detector.

        Args:
            detector_path (Optional[str]): path to the hihi detector. If not
                specified, looks for a file ./models/hihi.pb relative to the
                directory of this file.

            prediction_block_size (Optional[int]): how many consecutive
                windows of audio we average over to get a prediction.

            num_cores (Optional[int]): how many CPU cores to use for the
                tensorflow scoring - None is the default and uses all available
                cores.

        Raises:
            NotFoundError: if we can't find the file.
        """
        if not detector_path:
            detector_path = os.path.join(
                os.path.dirname(__file__), 'models', 'hihi.pb')

        # how does this resolve?
        super(HihiCNN, self).__init__(detector_path, num_cores=num_cores)

        # some constants
        self._audio_chunk_size = 16128  # how many samples we deal with at once
        self._audio_framerate = 24000  # expected sample rate of the audio
        self._audio_hop_size = self._audio_chunk_size // 1
        self._prediction_block = prediction_block_size

    def score(self, audio):
        """score some audio using the tensorflow graph"""
        # prepare the audio (convert to floating point, ensure the framerate)
        audio_data = audio.audio  # assume 16 bit (the loading code does)
        audio_data = audio_data.astype(np.float32) / (2**15)

        if audio.framerate != self._audio_framerate:
            print('framerate is wrong (expected {}, found {})'.format(
                self._audio_framerate, audio.framerate))

        result = self.average_graph_outputs(audio_data,
                                            self._audio_chunk_size,
                                            self._audio_hop_size,
                                            self._prediction_block)
        return result
