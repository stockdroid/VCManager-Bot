from pyrogram import Client
from pyrogram.types import Message

import shared


async def setlimit(client: Client, message: Message):
    shared.limit = int(message.text.split(" ")[1])
    await message.reply_text(f"new VC Limit: {shared.limit}")