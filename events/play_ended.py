from pytgcalls.implementation.group_call import GroupCall

import shared


async def play_ended(group_call: GroupCall, filename: str):
    shared.time_started = 0