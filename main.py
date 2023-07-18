import asyncio
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pytgcalls import PyTgCalls, idle
from sanic import Sanic

import endpoints.root
import endpoints.root as root
import shared
from commands.movetotop import movetotop
from commands.setlimit import setlimit
from commands.vclimit import vclimit
from events.vc_part_change import part_change
from shared import DEV_MODE
import threading

load_dotenv()

PHONE_NUMBER = os.environ.get(f"PHONE{'_DEV' if DEV_MODE else ''}")
API_ID = os.environ.get(f"API_ID")
API_HASH = os.environ.get(f"API_HASH")

tg_app = Client("vcmanager", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER)
call_py = PyTgCalls(tg_app)

api = Sanic.get_app(
    "vcmanApi",
    force_create=True,
)


@call_py.on_participants_change()
async def vc_partecipants_change(client: PyTgCalls, update):
    await part_change(client, update, tg_app)


tg_app.add_handler(MessageHandler(
    vclimit,
    filters.command("vclimit")
), shared.GROUP_ID)

tg_app.add_handler(MessageHandler(
    setlimit,
    filters.command("setlimit")
), shared.GROUP_ID)

tg_app.add_handler(MessageHandler(
    movetotop,
    filters.command("movetotop")
), shared.GROUP_ID)

api.blueprint(endpoints.root.rootBp)


if __name__ == "__main__":
    config = uvicorn.Config("main:api", port=5889, log_level="debug", use_colors=True, reload=True)
    server = uvicorn.Server(config)

    call_py.start()
    threading.Thread(target=server.run, daemon=True).start()
    idle()
