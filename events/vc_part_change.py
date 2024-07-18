import json
from typing import List

import pyrogram
from pyrogram import Client
from pyrogram.raw.functions.phone import EditGroupCallParticipant
from pyrogram.raw.types import InputGroupCall
from pytgcalls.implementation.group_call import GroupCall
from pytgcalls.mtproto.data import GroupCallParticipantWrapper

import shared
from ext.log_helper import part_change_log, vc_action_log
from shared import unmuted_list
from shared import tg_app as app


async def part_change(context: GroupCall, participants: List[GroupCallParticipantWrapper]):
    if context.full_chat.id == int(str(shared.GROUP_ID).replace("-100", "")):
        uname = ""
        name = ""
        last_name = ""

        bot = await app.get_me()
        bot_id = bot.id

        async for member in app.get_chat_members(shared.GROUP_ID):
            if member.user.id == participants[0].peer.user_id:
                uname = member.user.username
                name = str(member.user.first_name or "")
                last_name = str(member.user.last_name or "")

        if participants[0].peer.user_id == bot_id:
            return

        peer = await app.resolve_peer(uname)

        if not participants[0].left and \
                not participants[0].just_joined and \
                participants[0].peer.user_id in shared.whitelist:
            if participants[0].muted:
                if participants[0].peer.user_id in shared.unmuted_ghost_list:
                    shared.unmuted_ghost_list.remove(participants[0].peer.user_id)
            else:
                shared.unmuted_ghost_list.append(participants[0].peer.user_id)
            for ws in shared.ws_list:
                await ws.send(
                    json.dumps({
                        "action": f"{'MUTE' if participants[0].muted else 'UNMUTE'}_USER",
                        "data": {
                            "user_id": participants[0].peer.user_id,
                            "username": uname
                        }
                    })
                )

        if not participants[0].left and \
                not participants[0].is_self and \
                participants[0].raise_hand_rating is None and \
                participants[0].peer.user_id not in shared.unmuted_ghost_list and \
                participants[0].peer.user_id not in shared.whitelist and \
                participants[0].peer.user_id not in shared.force_muted:
            await app.invoke(EditGroupCallParticipant(
                call=context.full_chat.call,
                participant=peer,
                muted=True
            ))
            await vc_action_log(True, peer.user_id, uname, name, last_name)

        if not participants[0].left and \
                participants[0].raise_hand_rating is None and \
                participants[0].peer.user_id not in shared.unmuted_ghost_list and \
                participants[0].peer.user_id not in shared.joined_list:
            await part_change_log(True, peer.user_id, uname, name, last_name)
            shared.joined_list.append(participants[0].peer.user_id)

        if participants[0].raise_hand_rating is not None:
            group_call: InputGroupCall = context.full_chat.call
            participants_to_loop = await app.invoke(pyrogram.raw.functions.phone.GetGroupParticipants(
                call=group_call, ids=[], sources=[], offset="", limit=-1
            ))
            for participant in participants_to_loop.participants:
                if not participant.muted and participant.peer.user_id not in shared.whitelist:
                    if participant.peer.user_id not in unmuted_list:
                        unmuted_list.append(participant.peer.user_id)
                if participant.peer.user_id not in shared.unmuted_ghost_list:
                    shared.unmuted_ghost_list.append(participant.peer.user_id)

            if (len(unmuted_list) - 1 < shared.limit or participants[0].peer.user_id in shared.whitelist) and \
                    participants[0].peer.user_id not in shared.force_muted:
                unmuted_list.append(peer.user_id)
                shared.unmuted_ghost_list.append(peer.user_id)
                await app.invoke(EditGroupCallParticipant(
                    call=context.full_chat.call,
                    participant=peer,
                    muted=False
                ))
                await vc_action_log(False, peer.user_id, uname, name, last_name)

            else:
                if participants[0].peer.user_id not in shared.muted_queue \
                        and participants[0].peer.user_id not in shared.force_muted:
                    shared.muted_queue.append(peer)

        elif participants[0].left:
            await part_change_log(False, peer.user_id, uname, name, last_name)
            if peer.user_id in shared.joined_list:
                shared.joined_list.remove(peer.user_id)
            try:
                if peer.user_id in unmuted_list:
                    unmuted_list.remove(peer.user_id)
                if peer.user_id in shared.unmuted_ghost_list:
                    shared.unmuted_ghost_list.remove(peer.user_id)
            except ValueError:
                pass
            group_call: InputGroupCall = context.full_chat.call
            participantstoloop = await app.invoke(pyrogram.raw.functions.phone.GetGroupParticipants(
                call=group_call, ids=[], sources=[], offset="", limit=-1
            ))
            for participant in participantstoloop.participants:
                if not participant.muted and participant.peer.user_id not in shared.whitelist:
                    if participant.peer.user_id not in unmuted_list:
                        unmuted_list.append(participant.peer.user_id)
                        shared.unmuted_ghost_list.append(participant.peer.user_id)

            if len(shared.muted_queue) != 0 and len(unmuted_list) - 1 < shared.limit:
                to_unmute = shared.muted_queue[0]
                shared.muted_queue.pop(0)
                unmuted_list.append(to_unmute.user_id)
                shared.unmuted_ghost_list.append(to_unmute.user_id)
                await app.invoke(EditGroupCallParticipant(
                    call=context.full_chat.call,
                    participant=to_unmute,
                    muted=False
                ))
                await vc_action_log(False, peer.user_id, uname, name, last_name)
