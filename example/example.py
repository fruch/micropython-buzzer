import random
import logging

from pyb import Timer, Pin

from buzzer import BuzzerPlayer, songs


logger = logging.getLogger(__name__)

class RgbLed(object):
    def __init__(self, r_pin, g_pin, b_pin):
        self.timer = Timer(2, freq=300)
        self.r_ch = self.timer.channel(1, Timer.PWM, pin=r_pin, pulse_width=0)
        self.g_ch = self.timer.channel(3, Timer.PWM, pin=g_pin, pulse_width=0)
        self.b_ch = self.timer.channel(2, Timer.PWM, pin=b_pin, pulse_width=0)

    def red(self, i):
        self.r_ch.pulse_width_percent(i)

    def blue(self, i):
        self.b_ch.pulse_width_percent(i)

    def green(self, i):
        self.g_ch.pulse_width_percent(i)

    def off(self):
        self.red(0)
        self.green(0)
        self.blue(0)


class deque:

    def __init__(self, iterable=None, maxlength=None):
        if iterable is None:
            self.q = []
        else:
            self.q = list(iterable)
        self.maxlength = maxlength

    def popleft(self):
        return self.q.pop(0)

    def popright(self):
        return self.q.pop()

    def pop(self):
        return self.q.pop()

    def append(self, a):
        if len(self.q) == self.maxlength:
            self.popleft()
        self.q.append(a)

    def appendleft(self, a):
        if len(self.q) == self.maxlength:
            self.popright()
        self.q.insert(0, a)

    def extend(self, a):
        if len(self.q) == self.maxlength:
            for _ in a:
                self.popleft()
        self.q.extend(a)

    def __len__(self):
        return len(self.q)

    def __bool__(self):
        return bool(self.q)

    def __iter__(self):
        yield from self.q

    def __str__(self):
        return 'deque({})'.format(self.q)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    rgb = RgbLed(Pin('X1'), Pin('X4'), Pin('X3'))
    sofar = deque(maxlength=16)

    def blink_led(freq):
        if freq == 0:
            rgb.off()
            return

        sofar.append(freq)
        val = (freq - min(sofar)) / max(sofar) * 100
        logger.debug(str(val))
        m = random.randint(1, 3)
        if m == 1: rgb.red(val); rgb.blue(0);  rgb.green(0)
        if m == 2: rgb.blue(val); rgb.red(0); rgb.green(0)
        if m == 3: rgb.green(val); rgb.red(0); rgb.blue(0)

    buzz = BuzzerPlayer(callback=blink_led)

    try:
        while True:
            for song_name, v in songs.items():
                tempo, song = v
                buzz.play_nokia_tone(tempo=tempo, song=song, name=song_name)
    finally:
        buzz.channel.pulse_width_percent(0)
        rgb.off()


