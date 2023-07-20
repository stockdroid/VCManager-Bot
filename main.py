import threading
import types
from typing import List

import uvicorn
from pyrogram import filters, idle
from pyrogram.handlers import MessageHandler
from pyrogram.raw.base import Update
from pyrogram.raw.types import UpdateNewChannelMessage, MessageService, MessageActionGroupCall
from pytgcalls.implementation import group_call
from pytgcalls.implementation.group_call import GroupCall
from pytgcalls.mtproto.data import GroupCallParticipantWrapper
#from pytgcalls import PyTgCalls, idle
from sanic import Sanic

import endpoints.root
import shared
from commands.movetotop import movetotop
from commands.setlimit import setlimit
from commands.vclimit import vclimit
from endpoints.forcedmute import forcedmutesbp
from endpoints.limits import limitsbp
from endpoints.play import playbp
from endpoints.queue import queuebp
from endpoints.useractions import useractionsbp
from endpoints.utils import utilsbp
from endpoints.voicechat import voicechatbp
from endpoints.whitelist import whitelistbp
from events.play_ended import play_ended
from events.vc_part_change import part_change
from shared import call_py, tg_app

api = Sanic.get_app("vcmanApi", force_create=True,)


if shared.COMMANDS_ENABLED:
    tg_app.add_handler(MessageHandler(
        vclimit, filters.command("vclimit")
    ), shared.GROUP_ID)

    tg_app.add_handler(MessageHandler(
        setlimit, filters.command("setlimit")
    ), shared.GROUP_ID)

    tg_app.add_handler(MessageHandler(
        movetotop, filters.command("movetotop")
    ), shared.GROUP_ID)

blueprints = [
    endpoints.root.rootBp, limitsbp, queuebp, useractionsbp, whitelistbp, utilsbp, playbp, forcedmutesbp, voicechatbp
]
for blueprint in blueprints:
    api.blueprint(blueprint)
    print(f"LOADED BP: {blueprint.name}")

call_py.on_participant_list_updated(part_change)
call_py.on_playout_ended(play_ended)

@tg_app.on_raw_update(group=shared.GROUP_ID)
async def raw(_, update: Update, __, chats: dict):
    if type(update) == UpdateNewChannelMessage and int(str(shared.GROUP_ID).replace("-100", "")) in chats.keys():
        if type(update.message) == MessageService:
            if type(update.message.action) == MessageActionGroupCall:
                if update.message.action.duration is None:
                    await call_py.start(shared.GROUP_ID)

if __name__ == "__main__":
    config = uvicorn.Config("main:api", port=5889, log_level="debug", use_colors=True, reload=True)
    server = uvicorn.Server(config)

    tg_app.start()
    call_py.start(shared.GROUP_ID)
    threading.Thread(target=server.run, daemon=True).start()
    idle()
