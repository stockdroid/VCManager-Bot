from pyrogram import Client
from pyrogram.types import Message

from shared import muted_queue


async def movetotop(_: Client, message: Message):
    to_top = int(message.text.split(" ")[1])
    muted_queue.remove(to_top)
    muted_queue[0:] = to_top, *muted_queue[0:-1]
    await message.reply_text(f"moved to top: {to_top}")