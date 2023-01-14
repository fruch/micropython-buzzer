import os.path
import unittest

from buzzer import BuzzerPlayer, note_freq
from nokia_songs import songs as nokia_songs
import songs

#import logging
#logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)

PITCHHZ = {}
keys_s = ('a', 'a#', 'b', 'c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#')

for k in range(88):
    freq = int(27.5 * 2. ** (k / 12.))
    _oct = (k + 9) // 12
    note = '%s%d' % (keys_s[k % 12], _oct)
    PITCHHZ[note] = freq


class BuzzerTests(unittest.TestCase):
    sample_file = os.path.join(os.path.dirname(__file__), 'Zlilmehuvan.mid')
    nokia_file = os.path.join(os.path.dirname(__file__), 'star_wars.nokia')

    def test_00(self):
        for key, val in PITCHHZ.items():
            self.assertAlmostEqual(note_freq(key),  val, delta=2)

    @staticmethod
    def test_01_init_no_params():
        b = BuzzerPlayer()

    @staticmethod
    def test_02_init():
        b = BuzzerPlayer(1, 2, 4)

    @staticmethod
    def test_03_play_nokia_tone():
        buzz = BuzzerPlayer(1, 2, 4)
        song = nokia_songs['pink_panther']
        buzz.play_nokia_tone(song, name='pink_panther')

    @staticmethod
    def test_03_play_nokia_tone_esp8266():
        buzz = BuzzerPlayer(12, platform="esp8266")
        song = nokia_songs['pink_panther']
        buzz.play_nokia_tone(song, name='pink_panther')

    @staticmethod
    def test_03_play_nokia_tone_pyborad():
        buzz = BuzzerPlayer(1, 2, 4,  platform='pyboard')
        song = nokia_songs['pink_panther']
        buzz.play_nokia_tone(song, name='pink_panther')

    def test_03_play_nokie_tone_file(self):
        buzz = BuzzerPlayer(1, 2, 4)
        buzz.play_nokia_tone(buzz.from_file(self.nokia_file), name='star_wars')

    def test_04_play_midi(self):
        buzz = BuzzerPlayer()
        if hasattr(buzz, 'play_midi'):
            buzz.play_midi(self.sample_file, track=1)

    @staticmethod
    def test_05_play_rtttl():
        buzz = BuzzerPlayer()
        if hasattr(buzz, 'play_rtttl'):
            buzz.play_rtttl(songs.find('Entertainer'))


if __name__ == "__main__":
    unittest.main()
