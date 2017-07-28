import sys
from math import pow

try:
    import time
except ImportError:
    pass

try:
    import re
except ImportError:
    import ure as re

try:
   from midi import MidiFile
except ImportError:
    MidiFile = None

try:
   from rtttl import RTTTL
except ImportError:
    RTTTL = None

SAMPLING_RATE = 1000

names = ("c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b")

A4 = 440
C0 = A4 * pow(2, -4.75)

def note_freq(note):
    n, o = note[:-1], int(note[-1])
    index = names.index(n)
    return int(round(pow(2, (float(o * 12 + index) / 12.0)) * C0, 2))

def isplit(iterable, sep=None):
    r = ''
    for c in iterable:
        r += c
        if sep is None:
            if not c.strip():
                r = r[:-1]
                if r:
                    yield r
                    r = ''                    
        elif r.endswith(sep):
            r=r[:-len(sep)]
            yield r
            r = ''
    if r:
        yield r

class BuzzerPlayer(object):

    def __init__(self, pin="X8", timer_id=1, channel_id=1, callback=None, platform=None):

        if not platform:
            platform = sys.platform
            
        self.platform = platform
        
        if platform == "esp8266":
            from machine import PWM, Pin
            self.buzzer_pin = PWM(Pin(pin, Pin.OUT), freq=1000)

        elif platform == "pyboard":
            import pyb
            from pyb import Pin, Timer
            self.pyb = pyb
            self.sound_pin = Pin(pin)
            self.timer = Timer(timer_id, freq=10000)
            self.channel = self.timer.channel(1, Timer.PWM, pin=self.sound_pin, pulse_width=0)
                  
        self.callback = callback

    def play_nokia_tone(self, tempo, song, transpose=6, name="unkown"):
        
        pattern = "([0-9]*)(.*)([0-9]?)"
        def tune(): 
            for item in isplit(song):
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
                yield (pitch + octave, int(duration))
             
        self.play_tune(tempo, tune(), transpose=transpose, name=name)

    def tune(self, freq, duration=0, duty=30):
        if self.platform == "esp8266":
            self.buzzer_pin.freq(int(freq))
            self.buzzer_pin.duty(duty)
            time.sleep_ms(int(duration * 0.9))
            self.buzzer_pin.duty(0)
            time.sleep_ms(int(duration * 0.1))

        elif self.platform == "pyboard":
            self.timer.freq(freq)  # change frequency for change tone
            self.channel.pulse_width_percent(30)
            self.pyb.delay(duration)

        if callable(self.callback):
            self.callback(freq)
            
    def play_tune(self, tempo, tune, transpose=0, name="unknown"):

        print("\n== playing '%s' ==:" % name)
        full_notes_per_second = float(tempo) / 60 / 4
        full_note_in_samples = SAMPLING_RATE / full_notes_per_second

        for note_pitch, note_duration in tune:
            duration = int(full_note_in_samples / note_duration)

            if note_pitch == "r":
                self.tune(0, duration, 0)
            else:
                freq = note_freq(note_pitch)
                if transpose: freq *= 2 ** transpose
                print("%s " % note_pitch, end="")
                self.tune(freq, duration, 30)
                
        self.tune(0, 0, 0)

    if MidiFile:
        def play_midi(self, filename, track=1,  transpose=6):
            midi = MidiFile(filename)
            tune = midi.read_track(track)
            self.play_tune(midi.tempo, tune, transpose=transpose, name=filename)

    if RTTTL:
        def play_rtttl(self, input):
            tune = RTTTL(input)    
            for freq, msec in tune.notes():
                self.tune(freq, msec)

