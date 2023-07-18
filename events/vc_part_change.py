from typing import List

from pyrogram import Client
from pyrogram.raw.functions.phone import EditGroupCallParticipant
from pytgcalls import PyTgCalls
from pytgcalls.types import GroupCall, InputStream, JoinedGroupCallParticipant, LeftGroupCallParticipant

import shared


async def part_change(client: PyTgCalls, update, app: Client):
    if update.chat_id == shared.GROUP_ID:
        calls: List[GroupCall] = client.active_calls
        voice_chat = await client.app.get_full_chat(update.chat_id)

        found = False
        for call in calls:
            if call.chat_id == shared.GROUP_ID:
                found = True

        if not found:
            await client.join_group_call(update.chat_id, stream=InputStream())

        user_peer = await client.app.resolve_peer(update.participant.user_id)

        if type(update) == JoinedGroupCallParticipant:
            await app.invoke(
                EditGroupCallParticipant(
                    call=voice_chat,
                    participant=user_peer,
                    muted=True
                )
            )
        if update.participant.raised_hand:
            participants = await client.get_participants(shared.GROUP_ID)

            unmuted_count = -1  # 0 - 1 che è l'userbot
            for participant in participants:
                if not participant.muted_by_admin and participant.user_id not in shared.whitelist:
                    unmuted_count += 1

            if unmuted_count < shared.limit:
                await app.invoke(
                    EditGroupCallParticipant(
                        call=voice_chat,
                        participant=user_peer,
                        muted=False
                    )
                )
            else:
                shared.muted_queue.append(update.participant.user_id)

        elif type(update) == LeftGroupCallParticipant:
            if len(shared.muted_queue) != 0:
                to_unmute = shared.muted_queue[0]
                shared.muted_queue.pop(0)
                await app.invoke(
                    EditGroupCallParticipant(
                        call=voice_chat,
                        participant=await client.app.resolve_peer(to_unmute),
                        muted=False
                    )
                )