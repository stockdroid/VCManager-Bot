from pyrogram import Client
from pyrogram.types import Message

import shared


async def vclimit(_: Client, message: Message):
    await message.reply_text(f"VC Limit: {shared.limit}")
