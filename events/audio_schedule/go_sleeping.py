from ext.audio_manager import AudioManager


def go_to_sleep():
    print("going to sleep...")
    AudioManager().play("sleep_begin")
