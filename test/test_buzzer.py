import os.path
import unittest

from buzzer import BuzzerPlayer, songs

#import logging
#logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)

class BuzzerTests(unittest.TestCase):
    sample_file = os.path.join(os.path.dirname(__file__), 'Zlilmehuvan.mid')

    def test_01_init_no_params(self):
        b = BuzzerPlayer()

    def test_02_init(self):
        b = BuzzerPlayer(1,2,4)

    def test_03_play_nokia_tone(self):
        buzz = BuzzerPlayer(1,2,4)
        tempo, song = songs['pink_panther']
        buzz.play_nokia_tone(tempo, song, name='pink_panther')

    def test_04_play_midi(self):
        buzz = BuzzerPlayer()
        buzz.play_midi(self.sample_file, track=1)
        
if __name__ == "__main__":
    unittest.main()
