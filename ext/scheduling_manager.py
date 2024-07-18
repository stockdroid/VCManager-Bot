import asyncio
import schedule
import time

from events.audio_schedule.go_sleeping import go_to_sleep
from events.audio_schedule.middle_sleeping import while_sleeping
from events.audio_schedule.wake_up import wake_up
from ext.audio_manager import AudioManager

SLEEP_DURING_AUDIO_DUR = AudioManager().audio_duration("sleeping")
def run_async_function(coroutine):  
    if asyncio.iscoroutinefunction(coroutine):
        asyncio.run(coroutine())
    else:
        coroutine()

# la gianpiertolda va a dormire alle 10 e si alza alle 8
schedule.every().day.at("22:00").do(run_async_function, go_to_sleep)
schedule.every(SLEEP_DURING_AUDIO_DUR + 0.5).seconds.do(run_async_function, while_sleeping)
schedule.every().day.at("08:00").do(wake_up)

def init_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)