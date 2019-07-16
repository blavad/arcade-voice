import threading
# import contextlib
import subprocess
import itertools
import wave

from collections import namedtuple

SUPPORTED_FILETYPES = ('wav', 'raw', 'voc', 'au')

class AudioFormat(namedtuple('AudioFormat',
                             ['sample_rate_hz', 'num_channels', 'bytes_per_sample'])):
    @property
    def bytes_per_second(self):
        return self.sample_rate_hz * self.num_channels * self.bytes_per_sample

AudioFormat.CD = AudioFormat(sample_rate_hz=44100, num_channels=2, bytes_per_sample=2)

def arecord(fmt, filetype='raw', filename=None, device='default'):
    if fmt is None:
        raise ValueError('Format must be specified for recording.')

    if filetype not in SUPPORTED_FILETYPES:
        raise ValueError('File type must be %s.' % ', '.join(SUPPORTED_FILETYPES))

    cmd = ['arecord', '-q',
           '-D', device,
           '-t', filetype,
           '-c', str(fmt.num_channels),
           '-f', 's%d' % (8 * fmt.bytes_per_sample),
           '-r', str(fmt.sample_rate_hz)]

    if filename is not None:
        cmd.append(filename)

    return cmd


def wave_set_format(wav_file, fmt):
    wav_file.setnchannels(fmt.num_channels)
    wav_file.setsampwidth(fmt.bytes_per_sample)
    wav_file.setframerate(fmt.sample_rate_hz)

class Recorder:

    def __init__(self, ):
        self._process = None
        self._done = threading.Event()
        self._started = threading.Event()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.join()

    def record(self, fmt, chunk_duration_sec, device='default',
               num_chunks=None,
               on_start=None, on_stop=None, filename=None):

        chunk_size = int(chunk_duration_sec * fmt.bytes_per_second)
        cmd = arecord(fmt=fmt, device=device)

        wav_file = None
        if filename:
            wav_file = wave.open(filename, 'wb')
            wave_set_format(wav_file, fmt)

        self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        self._started.set()
        if on_start:
            on_start()
        try:
            for _ in (range(num_chunks) if num_chunks else itertools.count()):
                if self._done.is_set():
                    break
                data = self._process.stdout.read(chunk_size)
                if not data:
                    break
                if wav_file:
                    wav_file.writeframes(data)
                yield data
        finally:
            self._process.stdout.close()
            if on_stop:
                on_stop()
            if wav_file:
                wav_file.close()

    def done(self):
        self._done.set()

    def join(self):
        self._started.wait()
        self._process.wait()