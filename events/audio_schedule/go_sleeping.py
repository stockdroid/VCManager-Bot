from ext.audio_manager import AudioManager


def go_to_sleep():
    AudioManager().play("sleep_begin")
