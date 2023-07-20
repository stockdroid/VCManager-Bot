import threading

import uvicorn
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pytgcalls import PyTgCalls, idle
from sanic import Sanic

import endpoints.root
import shared
from commands.movetotop import movetotop
from commands.setlimit import setlimit
from commands.vclimit import vclimit
from endpoints.limits import limitsbp
from endpoints.play import playbp
from endpoints.queue import queuebp
from endpoints.useractions import useractionsbp
from endpoints.utils import utilsbp
from endpoints.whitelist import whitelistbp
from events.vc_part_change import part_change
from shared import call_py, tg_app

api = Sanic.get_app("vcmanApi", force_create=True,)


@call_py.on_participants_change()
async def vc_partecipants_change(client: PyTgCalls, update):
    await part_change(client, update, tg_app)


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

api.blueprint(endpoints.root.rootBp)
api.blueprint(limitsbp)
api.blueprint(queuebp)
api.blueprint(useractionsbp)
api.blueprint(whitelistbp)
api.blueprint(utilsbp)
api.blueprint(playbp)

if __name__ == "__main__":
    config = uvicorn.Config("main:api", port=5889, log_level="debug", use_colors=True, reload=True)
    server = uvicorn.Server(config)

    call_py.start()
    threading.Thread(target=server.run, daemon=True).start()
    idle()
