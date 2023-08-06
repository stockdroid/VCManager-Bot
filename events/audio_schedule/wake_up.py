from ext.audio_manager import AudioManager


def wake_up():
    print("woke up...")
    AudioManager().play("sleep_end")
