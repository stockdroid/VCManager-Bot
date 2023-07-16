import os

from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import Update, UpdatedGroupCallParticipant, GroupCall, InputStream

DEV_MODE = True
DEF_LIMIT = 2 if DEV_MODE else 30

load_dotenv()

PHONE_NUMBER = os.environ.get(f"PHONE{'_DEV' if DEV_MODE else ''}")
API_ID = os.environ.get(f"API_ID")
API_HASH = os.environ.get(f"API_HASH")

GROUP_ID = -939094139

limit = DEF_LIMIT
muted_queue = []

app = Client("vcmanager", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER)
call_py = PyTgCalls(app)

@app.on_message(filters.command("vclimit"))
async def vclimit(client: Client, message: Message):
    if message.chat.id == GROUP_ID:
        await message.reply_text(f"VC Limit: {limit}")

@app.on_message(filters.command("setlimit"))
async def setlimit(client: Client, message: Message):
    global limit
    if message.chat.id == GROUP_ID:
        limit = int(message.text.split(" ")[1])
        await message.reply_text(f"new VC Limit: {limit}")

@call_py.on_raw_update()
async def raw_update(client: PyTgCalls, update: Update):
    # basic logging
    if update.chat_id == GROUP_ID:
        print(update)

@call_py.on_participants_change()
async def vc_partecipants_change(client: PyTgCalls, update: UpdatedGroupCallParticipant):
    # basic logging
    if update.chat_id == GROUP_ID:
        await client.join_group_call(update.chat_id, stream=InputStream())
        if update.participant.raised_hand:
            # to be continued
            pass


call_py.run()
# app.run()
