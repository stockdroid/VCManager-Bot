import pyrogram
from pyrogram.raw.functions.phone import EditGroupCallParticipant
from pyrogram.raw.types import InputGroupCall
from pyrogram.raw.types.phone import GroupParticipants

import shared
from ext.audio_manager import AudioManager
from shared import tg_app, call_py

async def go_to_sleep():
    group_call: InputGroupCall = call_py.full_chat.call
    participantstoloop: GroupParticipants = await tg_app.invoke(pyrogram.raw.functions.phone.GetGroupParticipants(
        call=group_call, ids=[], sources=[], offset="", limit=-1
    ))

    shared.ex_limit = shared.limit
    shared.limit = 0
    
    for participant in participantstoloop.participants:
        if not participant.muted and not participant.is_self:
            await tg_app.invoke(EditGroupCallParticipant(
                call=group_call,
                participant=await tg_app.resolve_peer(participant.peer.user_id),
                muted=True
            ))

    print("going to sleep...")
    AudioManager().play("sleep_begin")