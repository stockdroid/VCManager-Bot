from ext.audio_manager import AudioManager


def wake_up():
    AudioManager().play("sleep_end")
