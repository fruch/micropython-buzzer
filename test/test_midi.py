import os.path
import unittest

from midi import MidiFile

#import logging
#logging.basicConfig(level=logging.DEBUG)


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class TestMidi(unittest.TestCase):
    sample_file = os.path.join(os.path.dirname(__file__), 'Zlilmehuvan.mid')

    def assertSequenceEqual(self, it1, it2):
        self.assertEqual(str(tuple(it1)), str(tuple(it2)))

    def test_01_init_no_file(self):
        with self.assertRaises(OSError):
            m = MidiFile('nonexist')

    def test_02_init(self):
        m = MidiFile(self.sample_file)

    def test_03_read_track(self):
        m = MidiFile(self.sample_file)
        notes = m.read_track(1)
        for n, expected in zip(notes[:4], (('r', 0.4343891402714933), ('c2', 1.116279069767441), ('r', 48.00000000000171), ('f1', 1.499999999999998))):
            self.assertEqual(n[0], expected[0])
            self.assertTrue(isclose(n[1], n[1]))

    def test_04_midi_offs(self):
        midi_file = os.path.join(os.path.dirname(__file__), 'clock_tower_short.mid')
        m = MidiFile(midi_file)
        notes = m.read_track(1)
        for n, expected in zip(notes[:4], (('r', 2.2857142857142856), ('f#5', 4.0), ('r', 8.0), ('d5', 4.0))):
            self.assertEqual(n[0], expected[0])
            self.assertTrue(isclose(n[1], n[1]))


if __name__ == "__main__":
    unittest.main()

