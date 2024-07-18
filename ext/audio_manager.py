import os
import time
from shared import call_py

class AudioManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init_singleton()
        return cls._instance

    def __init_singleton(self):
        self.reset()
        self.BIT_DEPTH = 16
        self.NUM_CHANNELS = 2
        self.SAMPLE_RATE = 48000
        self.audio_duration_cache = {}

    def reset(self):
        self.time_started = None
        self.time_at_pause = 0
        self.current_filename = None

    def play(self, filename: str):
        self.reset()
        self.current_filename = filename
        call_py.input_filename = f"./audio/{filename}.audio"
        call_py.restart_playout()
        self.time_started = time.time()
        call_py.play_on_repeat = False

    def loop(self, filename: str):
        self.reset()
        self.current_filename = filename
        call_py.input_filename = f"./audio/{filename}.audio"
        call_py.restart_playout()
        self.time_started = time.time()
        call_py.play_on_repeat = True

    def pause(self):
        if self.time_started:
            call_py.pause_playout()
            self.time_at_pause = time.time() - self.time_started

    def resume(self):
        if self.time_at_pause:
            call_py.resume_playout()
            self.time_started = time.time() - self.time_at_pause
            self.time_at_pause = 0


    def is_playing(self):
        if self.time_started and not self.time_at_pause:
            current_time = time.time()
            time_elapsed = current_time - self.time_started
            if self.current_filename:
                duration = self.audio_duration(self.current_filename)
                if time_elapsed < duration:
                    return True
        return False

    @staticmethod
    async def list_files():
        return os.listdir("./audio")

    def audio_duration(self, filename: str):
        if filename in self.audio_duration_cache:
            return self.audio_duration_cache[filename]
        size = os.path.getsize(f"./audio/{filename}.audio")
        duration = size / (self.NUM_CHANNELS * self.SAMPLE_RATE * (self.BIT_DEPTH / 8))
        self.audio_duration_cache[filename] = duration
        return duration

    async def time_elapsed(self):
        if self.time_started is None:
            return 0
        current_time = time.time()
        if self.time_at_pause:
            time_elapsed = self.time_at_pause
        else:
            time_elapsed = current_time - self.time_started
        if self.current_filename:
            duration = self.audio_duration(self.current_filename)
            if time_elapsed >= duration:
                self.reset()
                return 0
        return time_elapsed