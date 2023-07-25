from pytgcalls.implementation.group_call import GroupCall

import shared
from ext.log_helper import play_ended_log


async def play_ended(group_call: GroupCall, filename: str):
    shared.time_started = 0
    await play_ended_log()
