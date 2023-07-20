from pyrogram import Client
from pyrogram.raw.functions.phone import EditGroupCallParticipant
from pytgcalls import PyTgCalls
from pytgcalls.types import InputStream, JoinedGroupCallParticipant, LeftGroupCallParticipant

import shared
from shared import unmuted_list


async def part_change(client: PyTgCalls, update, app: Client):
    if update.chat_id == shared.GROUP_ID:
        voice_chat = await client._app.get_full_chat(update.chat_id)
        uname: str
        async for member in app.get_chat_members(update.chat_id):
            if member.user.id == update.participant.user_id:
                uname = member.user.username

        try:
            await client.join_group_call(update.chat_id, stream=InputStream())
        except:
            pass  # piangi

        if type(update) == JoinedGroupCallParticipant:
            await app.invoke(
                EditGroupCallParticipant(
                    call=voice_chat,
                    participant=await client._app.resolve_peer(uname),
                    muted=True
                )
            )

        if update.participant.raised_hand:
            participants = await client.get_participants(shared.GROUP_ID)
            for participant in participants:
                if not participant.muted_by_admin and participant.user_id not in shared.whitelist:
                    if participant.user_id not in unmuted_list:
                        unmuted_list.append(participant.user_id)

            if len(unmuted_list) - 1 < shared.limit or update.participant.user_id in shared.whitelist:
                await app.invoke(
                    EditGroupCallParticipant(
                        call=voice_chat,
                        participant=await client._app.resolve_peer(uname),
                        muted=False
                    )
                )
                unmuted_list.append(update.participant.user_id)
            else:
                if update.participant.user_id not in shared.muted_queue:
                    shared.muted_queue.append(update.participant.user_id)

        elif type(update) == LeftGroupCallParticipant:
            try:
                unmuted_list.remove(update.participant.user_id)
            except ValueError:
                pass
            # ricontrollo, in caso di doppio update, se il limite è raggiunto
            # e uso una lista locale per evitare problemi
            participants = await client.get_participants(shared.GROUP_ID)
            for participant in participants:
                if not participant.muted_by_admin and participant.user_id not in shared.whitelist:
                    if participant.user_id not in unmuted_list:
                        unmuted_list.append(participant.user_id)

            if len(shared.muted_queue) != 0 and len(unmuted_list) - 1 < shared.limit:
                to_unmute = shared.muted_queue[0]
                shared.muted_queue.pop(0)
                await app.invoke(
                    EditGroupCallParticipant(
                        call=voice_chat,
                        participant=await client._app.resolve_peer(to_unmute),
                        muted=False
                    )
                )
                unmuted_list.append(update.participant.user_id)
