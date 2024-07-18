from datetime import datetime, time
import asyncio
from pyrogram.raw.functions.phone import EditGroupCallParticipant
from pyrogram.raw.types import UpdateGroupCallParticipants
from shared import tg_app, call_py
from ext.audio_manager import AudioManager

audio_manager = AudioManager()

GO_SLEEP_DUR = audio_manager.audio_duration("sleep_begin")
WAKE_UP_DUR = audio_manager.audio_duration("sleep_end")
SLEEP_DURING_AUDIO_DUR = audio_manager.audio_duration("sleeping")

start_time = time(22, 0,  int(GO_SLEEP_DUR))
end_time = time(7, 59, 60 - int(SLEEP_DURING_AUDIO_DUR))

tolda_counter = 0
last_tolda_time = 0
last_handle_time = 0 


def is_time_between(begin_time, end_time, check_time=None):
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time

@tg_app.on_raw_update()
async def on_update(client, update, users, chats):
    global last_handle_time 

    if isinstance(update, UpdateGroupCallParticipants) and is_time_between(start_time, end_time):
        group_call = call_py.full_chat.call

        if hasattr(update, 'participants'):
            for participant in update.participants:
                if participant.raise_hand_rating is not None and not participant.is_self:
                    await client.invoke(EditGroupCallParticipant(
                        call=group_call,
                        participant=await tg_app.resolve_peer(participant.peer.user_id),
                        raise_hand=False
                    ))
                    # Controlla se sono passati almeno 6 secondi dall'ultima esecuzione
                    current_time = datetime.now().timestamp()
                    if current_time - last_handle_time >= 5 or current_time - last_handle_time == current_time:
                        last_handle_time = current_time
                        await handle_raise_hand(update)


async def handle_raise_hand(update):
    global tolda_counter

    for participant in update.participants:
        if participant.raise_hand_rating is not None and not participant.is_self:
            if tolda_counter % 2 == 0:
                audio_manager.play("tolda1")
                await asyncio.sleep(audio_manager.audio_duration("tolda1"))
            else:
                audio_manager.play("tolda2")
                await asyncio.sleep(audio_manager.audio_duration("tolda2"))

            tolda_counter += 1
            audio_manager.reset()
            await asyncio.sleep(1)
            asyncio.create_task(while_sleeping())

async def while_sleeping():
    if is_time_between(start_time, end_time) and not audio_manager.is_playing() and not audio_manager.current_filename in ["tolda1", "tolda2"]:
        print("sleep sfx...")
        audio_manager.loop("sleeping")
        await asyncio.sleep(SLEEP_DURING_AUDIO_DUR)
