from typing import List

import pyrogram
from pyrogram import Client
from pyrogram.raw.functions.phone import EditGroupCallParticipant
from pyrogram.raw.types import InputGroupCall
from pytgcalls.implementation.group_call import GroupCall
from pytgcalls.mtproto.data import GroupCallParticipantWrapper

import shared
from shared import unmuted_list
from shared import tg_app as app


async def part_change(context: GroupCall, participants: List[GroupCallParticipantWrapper]):
    if context.full_chat.id == int(str(shared.GROUP_ID).replace("-100", "")):
        uname = ""
        async for member in app.get_chat_members(shared.GROUP_ID):
            if member.user.id == participants[0].peer.user_id:
                uname = member.user.username

        peer = await app.resolve_peer(uname)
        if not participants[0].left and \
                not participants[0].is_self and \
                participants[0].raise_hand_rating is None and \
                participants[0].peer.user_id not in unmuted_list and \
                participants[0].peer.user_id not in shared.whitelist and \
                participants[0].peer.user_id not in shared.force_muted:
            await app.invoke(EditGroupCallParticipant(
                call=context.group_call,
                participant=peer,
                muted=True
            ))


        if participants[0].raise_hand_rating is not None: # è giusto?
            group_call: InputGroupCall = context.group_call
            participantstoloop = await app.invoke(pyrogram.raw.functions.phone.GetGroupParticipants(
                call = group_call, ids = [], sources = [], offset = "", limit=-1
            ))
            for participant in participantstoloop.participants:
                if not participant.muted and participant.peer.user_id not in shared.whitelist:
                    if participant.peer.user_id not in unmuted_list:
                        unmuted_list.append(participant.peer.user_id)

            if (len(unmuted_list) - 1 < shared.limit or participants[0].peer.user_id in shared.whitelist) and participants[0].peer.user_id not in shared.force_muted:
                unmuted_list.append(peer.user_id)
                await app.invoke(EditGroupCallParticipant(
                    call=context.group_call,
                    participant=peer,
                    muted=False
                ))

            else:
                if participants[0].peer.user_id not in shared.muted_queue and participants[0].peer.user_id not in shared.force_muted:
                    shared.muted_queue.append(peer)

        elif participants[0].left:
            try:
                unmuted_list.remove(peer.user_id)
            except ValueError:
                pass
            # ricontrollo, in caso di doppio update, se il limite è raggiunto
            # e uso una lista locale per evitare problemi
            group_call: InputGroupCall = context.group_call
            participantstoloop = await app.invoke(pyrogram.raw.functions.phone.GetGroupParticipants(
                call = group_call, ids = [], sources = [], offset = "", limit=-1
            ))
            for participant in participantstoloop.participants:
                if not participant.muted and participant.peer.user_id not in shared.whitelist:
                    if participant.peer.user_id not in unmuted_list:
                        unmuted_list.append(participant.peer.user_id)

            if len(shared.muted_queue) != 0 and len(unmuted_list) - 1 < shared.limit:
                to_unmute = shared.muted_queue[0]
                shared.muted_queue.pop(0)
                unmuted_list.append(to_unmute.user_id)
                await app.invoke(EditGroupCallParticipant(
                    call=context.group_call,
                    participant=to_unmute,
                    muted=False
                ))