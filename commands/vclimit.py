from pyrogram import Client
from pyrogram.types import Message

from shared import limit


async def vclimit(_: Client, message: Message):
    await message.reply_text(f"VC Limit: {limit}")