import shared
from ext.audio_manager import AudioManager
from shared import tg_app, call_py

import pyrogram
from pyrogram.raw.functions.phone import EditGroupCallParticipant
from pyrogram.raw.types import InputGroupCall
from pyrogram.raw.types.phone import GroupParticipants

def wake_up():
    group_call: InputGroupCall = call_py.full_chat.call
    participantstoloop: GroupParticipants = tg_app.invoke(pyrogram.raw.functions.phone.GetGroupParticipants(
        call=group_call, ids=[], sources=[], offset="", limit=-1
    ))

    if hasattr(shared, 'ex_limit'):
        shared.limit = shared.ex_limit

    for participant in participantstoloop.participants:
        if participant.muted and not participant.is_self:
             tg_app.invoke(EditGroupCallParticipant(
                call=group_call,
                participant= tg_app.resolve_peer(participant.peer.user_id),
                muted=False
            ))

    print("woke up...")
    AudioManager().play("sleep_end")
