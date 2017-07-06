import re
import logging

import pyb
from pyb import Pin, Timer

from .midi import MidiFile

logger = logging.getLogger(__name__)

# taken from http://nokia.nigelcoldwell.co.uk/tunes.html
songs = dict(
    pink_panther=(100, "8#g1 2a1 8b1 2c2 8#g1 8a1 8b1 8c2 8f2 8e2 8a1 8c2 8e2 2#d2 16d2 16c2 16a1 8g1 1a1 8#g1 2a1 8b1 2c2 8#g1 8a1 8b1 8c2 8f2 8e2 8c2 8e2 8a2 1#g2 8#g1 2a1 8b1 2c2 16#g1 8a1 8b1 8c2 8f2 8e2 8a1 8c2 8e2 2#d2 8d2 16c2 16a1"),
    imperial_march=(100, "4e1 4e1 4e1 8c1 16- 16g1 4e1 8c1 16- 16g1 4e1 4- 4b1 4b1 4b1 8c2 16- 16g1 4#d1 8c1 16- 16g1 4e1 8-"),
    pulp_fiction=(113, "16f1 16f1 16f1 16f1 16f1 16f1 16f1 16f1 16a1 16a1 16a1 16a1 16#a1 16#a1 16#a1 16#a1 16c2 16c2 16c2 16c2 16c2 16c2 16c2 16f1 16e2 16e2 16e2 16e2 16#c2 16#c2 16#c2 16#c2 16c2 16c2 16c2 16c2 16c2 16c2 16c2 16c2 16c2 16c2 16c2 16c2 16c2 16c2 16c2 16c2 16c2 16c2"),
    american_pie=(125, "2g2 4f2 8f2 8f2 8e2 32d2 16- 32- 8c2 8d2 4- 8g2 32g2 16- 32- 32g2 16- 32- 32g2 16- 32- 32g2 16- 32- 32g2 16- 32- 32f2 16- 32- 32f2 16- 32- 32f2 16- 32- 32f2 16- 32- 8e2 32d2 16- 32- 8c2 8g1"),
    sex_bomb=(125, "8c2 8- 4a1 8c2 8- 4a1 8- 4d2 8c2 4e2 16c2 16d2 4e2 4c2 8c2 8c2 8c2 8c2 8c2 8c2 8a1 8c2 8a1 8a1 8g1 4a1 8c2 8- 4a1 8c2 8- 4a1 8- 4d2 8c2 4e2 4c2 8- 4c2 8a1 8c2 8a1 8g1 16- 8#g1 16- 4a1"),
    colors_of_the_night=(80, "2#g2 8c2 2#c2 4g2 8#g2 4#a2 8c2 8#a1 2#g1 2f2 8#g1 2g1 8f2 16e2 8f2 2g2 2#g2 8c2 2#c2 4g2 8#g2 4#a2 8c2 8#a1 2#g1 2f2 8#g1 2g1 8f2 8e2 8f2 2g2 8#a1 8c2 8c2 4c2 4#c2 2#a2 8#a1 8#a2 8#a2 4#a2 4c2 4#a2 8#g2 4g2 2#g2 8c2 8c2 4c2"),
)

SAMPLING_RATE = 1000

PITCHHZ = {}
keys_s = ('a', 'a#', 'b', 'c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#')

for k in range(88):
    freq = 27.5 * 2. ** (k / 12.)
    oct = (k + 9) // 12
    note = '%s%u' % (keys_s[k % 12], oct)
    PITCHHZ[note] = freq


class BuzzerPlayer(object):
    def __init__(self, pin="X8", timer_id=1, channel_id=1, callback=None):
        self.sound_pin = Pin(pin)
        self.timer = Timer(timer_id, freq=10000)
        self.channel = self.timer.channel(1, Timer.PWM, pin=self.sound_pin, pulse_width=0)
        self.callback = callback

    def play_nokia_tone(self, tempo, song, transpose=6, name="unkown"):
        tune = []
        pattern = "([0-9]*)(.*)([0-9]?)"
        for item in song.split():
            match = re.match(pattern, item)
            duration = match.group(1)
            pitch = match.group(2)
            octave = match.group(3)

            if pitch == "-":
                pitch = "r"
            if pitch.startswith("#"):
                pitch = pitch[1] + "#" + pitch[2:]
            dotted = pitch.startswith(".")
            duration = -int(duration) if dotted else int(duration)

            tune.append((pitch + octave, int(duration)))
        logger.debug("Tune: %s", tune)

        self.play_tune(tempo, tune, transpose=transpose, name=name)


    def play_tune(self, tempo, tune, transpose=6, name="unknown"):

        full_notes_per_second = float(tempo) / 60 / 4
        full_note_in_samples = SAMPLING_RATE / full_notes_per_second

        for note_pitch, note_duration in tune:
            # note_duration is 1, 2, 4, 8, ... and actually means 1, 1/2, 1/4, ...
            duration = int(full_note_in_samples / note_duration)

            if note_pitch == "r":

                self.channel.pulse_width_percent(0)
                pyb.delay(duration)
                if callable(self.callback):
                    self.callback(0)
            else:
                freq = PITCHHZ[note_pitch]
                freq *= 2 ** transpose
                logger.debug("playing %s : %s", name, note_pitch)
                self.timer.freq(freq)  # change frequency for change tone
                self.channel.pulse_width_percent(30)
                pyb.delay(duration)
                if callable(self.callback):
                    self.callback(freq)


    def play_midi(self, filename, track=1,  transpose=6):
        midi = MidiFile(filename)
        tune = midi.read_track(track)
        self.play_tune(midi.tempo, tune, transpose=transpose, name=filename)



