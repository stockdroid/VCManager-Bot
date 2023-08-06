from datetime import datetime, time

from ext.audio_manager import AudioManager

GO_SLEEP_DUR = AudioManager().audio_duration("sleep_begin")
WAKE_UP_DUR = AudioManager().audio_duration("sleep_end")


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def while_sleeping():
    if is_time_between(time(1, 40, int(GO_SLEEP_DUR)), time(1, 41, 60 - int(WAKE_UP_DUR))):
        print("sleep sfx...")
        AudioManager().play("orgasm")
