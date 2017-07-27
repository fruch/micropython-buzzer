import os.path
import unittest

from midi import MidiFile

#import logging
#logging.basicConfig(level=logging.DEBUG)

class TestMidi(unittest.TestCase):
    sample_file = os.path.join(os.path.dirname(__file__), 'Zlilmehuvan.mid')

    def assertSequenceEqual(self, it1, it2):
        self.assertEqual(str(tuple(it1)), str(tuple(it2)))

    def test_01_init_no_file(self):
        with self.assertRaises(OSError):
            m =  MidiFile('nonexist')

    def test_02_init(self):
        m =  MidiFile(self.sample_file)

    def test_03_read_track(self):
        m =  MidiFile(self.sample_file)
        notes = m.read_track(1)
        self.assertSequenceEqual(notes[:4], [('r', 0.4343891402714934), ('c2', 1.11627906976744), ('r', 48.00000000000068), ('f1', 1.499999999999999)])

if __name__ == "__main__":
    unittest.main()

