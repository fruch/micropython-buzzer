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
    oct = (k + 9) // 12
    note = '%s%d' % (keys_s[k % 12], oct)
    print(note)
    PITCHHZ[note] = freq

class BuzzerTests(unittest.TestCase):
    sample_file = os.path.join(os.path.dirname(__file__), 'Zlilmehuvan.mid')

    def test_00(self):
        for k, v  in PITCHHZ.items():
            self.assertAlmostEqual(note_freq(k),  v, delta=2)

    def test_01_init_no_params(self):
        b = BuzzerPlayer()

    def test_02_init(self):
        b = BuzzerPlayer(1,2,4)

    def test_03_play_nokia_tone(self):
        buzz = BuzzerPlayer(1,2,4)
        tempo, song = nokia_songs['pink_panther']
        buzz.play_nokia_tone(tempo, song, name='pink_panther')

    def test_03_play_nokia_tone_esp8266(self):
        buzz = BuzzerPlayer(12, platform="esp8266")
        tempo, song = nokia_songs['pink_panther']
        buzz.play_nokia_tone(tempo, song, name='pink_panther')

    def test_03_play_nokia_tone_pyborad(self):
        buzz = BuzzerPlayer(1,2,4,  platform='pyboard')
        tempo, song = nokia_songs['pink_panther']
        buzz.play_nokia_tone(tempo, song, name='pink_panther')

    def test_04_play_midi(self):
        buzz = BuzzerPlayer()
        if hasattr(buzz, 'play_midi'):
            buzz.play_midi(self.sample_file, track=1)
            
    def test_05_play_rtttl(self):
        buzz = BuzzerPlayer()
        if hasattr(buzz, 'play_rtttl'):
            buzz.play_rtttl(songs.find('Entertainer'))


if __name__ == "__main__":
    unittest.main()
