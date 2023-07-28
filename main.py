import json
import os
import threading

import requests
import uvicorn
from dotenv import load_dotenv
from jwt.algorithms import RSAAlgorithm
from pyrogram import filters, idle
from pyrogram.handlers import MessageHandler
from pyrogram.raw.base import Update
from pyrogram.raw.types import UpdateNewChannelMessage, MessageService, MessageActionGroupCall
from sanic import Sanic

import shared
from commands.movetotop import movetotop
from commands.setlimit import setlimit
from commands.vclimit import vclimit
from endpoints.forcedmute import forcedmutesbp
from endpoints.limits import limitsbp
from endpoints.play import playbp
from endpoints.queue import queuebp
from endpoints.root import rootBp
from endpoints.useractions import useractionsbp
from endpoints.utils import utilsbp
from endpoints.voicechat import voicechatbp
from endpoints.whitelist import whitelistbp
from events.net_change import net_change
from events.play_ended import play_ended
from events.vc_part_change import part_change
from ext.ws_stream import ws_bp
from shared import call_py, tg_app

api = Sanic.get_app("vcmanApi", force_create=True)
load_dotenv()

api.config.CORS_ORIGINS = "*"
api.config.CORS_SEND_WILDCARD = True
api.config.OAS_UI_DEFAULT = "swagger"

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
    rootBp, limitsbp, queuebp, useractionsbp, whitelistbp,
    utilsbp, playbp, forcedmutesbp, voicechatbp, ws_bp
]
for blueprint in blueprints:
    api.blueprint(blueprint)
    print(f"LOADED BP: {blueprint.name}")

call_py.on_participant_list_updated(part_change)
call_py.on_playout_ended(play_ended)
call_py.on_network_status_changed(net_change)

@tg_app.on_raw_update(group=shared.GROUP_ID)
async def raw(_, update: Update, __, chats: dict):
    if type(update) == UpdateNewChannelMessage and int(str(shared.GROUP_ID).replace("-100", "")) in chats.keys():
        if type(update.message) == MessageService:
            if type(update.message.action) == MessageActionGroupCall:
                if update.message.action.duration is None:
                    await call_py.start(shared.GROUP_ID)


if shared.ENABLE_CF_AUTH:
    print("Auth enabled")
    res = requests.get(f"https://{os.environ.get('CF_URL')}/cdn-cgi/access/certs")
    jwk_set = res.json()
    algo = RSAAlgorithm(RSAAlgorithm.SHA256)
    for key_dict in jwk_set['keys']:
        public_key = algo.from_jwk(json.dumps(key_dict))
        shared.public_keys.append(public_key)
    print("Loaded public keys from CF")
    api.ext.openapi.add_security_scheme(
        "token",
        type="http",
        scheme="bearer",
        bearer_format="JWT",
        description="Cloudflare access auth token"
    )
    print("Added security scheme")
else:
    print("Auth disabled, this api is open without authorization!")

if __name__ == "__main__":
    config = uvicorn.Config("main:api", host="0.0.0.0", port=5889, use_colors=True, reload=True)
    server = uvicorn.Server(config)

    tg_app.start()
    threading.Thread(target=server.run, daemon=True).start()
    idle()
