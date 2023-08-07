import shared
from ext.audio_manager import AudioManager


def wake_up():
    shared.force_muted = shared.exforce_muted
    shared.exforce_muted = []

    print("woke up...")
    AudioManager().play("sleep_end")
