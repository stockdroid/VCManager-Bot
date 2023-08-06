import os
import time

from shared import call_py


class AudioManager(object):
    _instance = None

    def __init__(self):
        self.time_started = 0
        self.time_at_pause = 0
        self.BIT_DEPTH = 16
        self.NUM_CHANNELS = 2
        self.SAMPLE_RATE = 48000

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def play(self, filename: str):
        self.time_started = 0
        self.time_at_pause = 0
        call_py.input_filename = f"./audio/{filename}.audio"
        call_py.restart_playout()
        self.time_started = time.time()
        call_py.play_on_repeat = False

    def pause(self):
        call_py.pause_playout()
        self.time_at_pause = time.time() - self.time_started

    def resume(self):
        call_py.resume_playout()
        if self.time_at_pause != 0:
            self.time_started = time.time() - self.time_at_pause
            self.time_at_pause = 0

    @staticmethod
    async def list_files():
        return os.listdir("./audio")

    async def audio_duration(self, filename: str):
        size = os.path.getsize(f"./audio/{filename}.audio")
        return size / (self.NUM_CHANNELS * self.SAMPLE_RATE * (self.BIT_DEPTH / 8))

    async def time_elapsed(self):
        if self.time_at_pause != 0:
            time_elapsed = self.time_at_pause
        else:
            time_elapsed = time.time() - self.time_started

        return time_elapsed
