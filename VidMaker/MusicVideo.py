import aubio
import wave
import math
import struct


def create_sine_wave(freq, samplerate, nframes, nchannels):
    """ create a pure tone (without numpy) """
    _x = [0.7 * math.sin(2. * math.pi * freq * t / float(samplerate))
          for t in range(nframes)]
    _x = [int(a * 32767) for a in _x]
    _x = b''.join([b''.join([struct.pack('h', v)
                             for _ in range(nchannels)])
                   for v in _x])
    return _x


def create_test_sound(pathname, freq=441, duration=None,
                      framerate=44100, nchannels=2):
    """ create a sound file at pathname, overwriting exiting file """
    sampwidth = 2
    nframes = duration or framerate  # defaults to 1 second duration
    fid = wave.open(pathname, 'w')
    fid.setnchannels(nchannels)
    fid.setsampwidth(sampwidth)
    fid.setframerate(framerate)
    fid.setnframes(nframes)
    frames = create_sine_wave(freq, framerate, nframes, nchannels)
    fid.writeframes(frames)
    fid.close()
    return 0

s = aubio.source('BrakaNova(2).wav')
print(aubio.freq2note(522))