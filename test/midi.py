import struct
import logging

logger = logging.getLogger(__name__)


class Note(object):
    """
    Represents a single MIDI note
    """

    note_names = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    
    def __init__(self, channel, pitch, velocity, start, duration = 0):
        self.channel = channel
        self.pitch = pitch
        self.velocity = velocity
        self.start = start
        self.duration = duration
    
    def __str__(self):
        s = Note.note_names[(self.pitch - 9) % 12]
        s += str(self.pitch // 12 - 1)
        s += " " + str(self.velocity)
        s += " " + str(self.start) + " " + str(self.start + self.duration) + " "
        return s
    
    def get_end(self):
        return self.start + self.duration


class MidiFile(object):
    """
    Represents the notes in a MIDI file
    """

    @staticmethod
    def read_byte(file):
        return struct.unpack('B', file.read(1))[0]
    
    def read_variable_length(self, file, counter):
        counter -= 1
        num = self.read_byte(file)
        
        if num & 0x80:
            num = num & 0x7F
            while True:
                counter -= 1
                c = self.read_byte(file)
                num = (num << 7) + (c & 0x7F)
                if not (c & 0x80):
                    break
        
        return num, counter
    
    def __init__(self, file_name):
        self.tempo = 120
        self.file_name = file_name
        file = None
        try:
            file = open(self.file_name, 'rb')
            if file.read(4) != b'MThd': raise Exception('Not a MIDI file')
            size = struct.unpack('>i', file.read(4))[0]
            if size != 6: raise Exception('Unusual MIDI file with non-6 sized header')
            self.format = struct.unpack('>h', file.read(2))[0]
            self.track_count = struct.unpack('>h', file.read(2))[0]
            self.time_division = struct.unpack('>h', file.read(2))[0]
        finally:
            if file:
                file.close()

    def read_track(self, track_num=1):
        file = None
        try:
            file = open(self.file_name, 'rb')
            if file.read(4) != b'MThd': raise Exception('Not a MIDI file')
            size = struct.unpack('>i', file.read(4))[0]
            if size != 6: raise Exception('Unusual MIDI file with non-6 sized header')
            self.format = struct.unpack('>h', file.read(2))[0]
            self.track_count = struct.unpack('>h', file.read(2))[0]
            self.time_division = struct.unpack('>h', file.read(2))[0]

            # Now to fill out the arrays with the notes
            tracks = []
            for i in range(0, self.track_count):
                tracks.append([])

            for nn, track in enumerate(tracks):
                abs_time = 0.

                if file.read(4) != b'MTrk': raise Exception('Not a valid track')
                size = struct.unpack('>i', file.read(4))[0]

                # To keep track of running status
                last_flag = None
                while size > 0:
                    delta, size = self.read_variable_length(file, size)
                    delta /= float(self.time_division)
                    abs_time += delta

                    size -= 1
                    flag = self.read_byte(file)
                    # Sysex messages
                    if flag == 0xF0 or flag == 0xF7:
                        # print "Sysex"
                        while True:
                            size -= 1
                            if self.read_byte(file) == 0xF7: break
                    # Meta messages
                    elif flag == 0xFF:
                        size -= 1
                        type = self.read_byte(file)
                        if type == 0x2F:    # end of track event
                            self.read_byte(file)
                            size -= 1
                            break
                        logger.debug("Meta: %s", str(type))
                        length, size = self.read_variable_length(file, size)
                        message = file.read(length)
                        # if type not in [0x0, 0x7, 0x20, 0x2F, 0x51, 0x54, 0x58, 0x59, 0x7F]:
                        logger.debug("%s %s", length, message)
                        if type == 0x51:    # qpm/bpm
                            # http://www.recordingblogs.com/sa/Wiki?topic=MIDI+Set+Tempo+meta+message
                            self.tempo = 6e7 / struct.unpack('>i', b'\x00' + message)[0]
                            logger.debug("tempo = %sbpm", self.tempo)
                    # MIDI messages
                    else:
                        if flag & 0x80:
                            type_and_channel = flag
                            size -= 1
                            param1 = self.read_byte(file)
                            last_flag = flag
                        else:
                            type_and_channel = last_flag
                            param1 = flag
                        type = ((type_and_channel & 0xF0) >> 4)
                        channel = type_and_channel & 0xF
                        if type == 0xC: # detect MIDI program change
                            logger.debug("program change, channel %s = %s", channel, param1)
                            continue
                        size -= 1
                        param2 = self.read_byte(file)
                        
                        # detect MIDI ons and MIDI offs
                        if type == 0x9:
                            note = Note(channel, param1, param2, abs_time)
                            if nn == track_num:
                                logger.debug("%s", note)
                                track.append(note)

                        elif type == 0x8:
                            for note in reversed(track):
                                if note.channel == channel and note.pitch == param1:
                                    note.duration = abs_time - note.start
                                    break

        finally:
            if file: 
                file.close()
    
        return self.parse_into_song(tracks[track_num])

    def parse_into_song(self, track):
        notes = {}
        song = []
        last2 = 0

        def getnote(q):
            for x in q.keys():
                if q[x] > 0:
                    return x
            return None
    
        for nn in track:
            nn = str(nn).split()
            start, stop = float(nn[2]), float(nn[3])
    
            if start != stop:   # note ends because of NOTE OFF event
                if last2 > -1 and start - last2 > 0:
                    song.append(('r', getdur(last2, start)))
                song.append((nn[0].lower(), getdur(start, stop)))
                last2 = stop
            elif float(nn[1]) == 0 and notes.get(nn[0].lower(), -1) >= 0: # note ends because of NOTE ON with velocity = 0
                if last2 > -1 and notes[nn[0].lower()] - last2 > 0:
                    song.append(('r', getdur(last2, notes[nn[0].lower()])))
                song.append((nn[0].lower(), getdur(notes[nn[0].lower()], start)))
                notes[nn[0].lower()] = -1
                last2 = start
            elif float(nn[1]) > 0 and notes.get(nn[0].lower(), -1) == -1: # note ends because of new note
                old = getnote(notes)
                if old != None:
                    if notes[old] != start:
                        song.append((old, getdur(notes[old], start)))
                    notes[old] = -1
                elif start - last2 > 0:
                    song.append(('r', getdur(last2, start)))
                notes[nn[0].lower()] = start
                last2 = start

        return song    


def getdur(a, b):
    """
    Calculate note length for PySynth"
    """

    return 4 / (b - a)

