from typing import AsyncGenerator
from telegram import ChatMember, User
from shared import tg_app, GROUP_ID


async def get_user(user_id: int) -> User:
    users_in_group: AsyncGenerator[ChatMember, None] = tg_app.get_chat_members(GROUP_ID)
    return [x.user async for x in users_in_group if x.user.id == user_id][0]


async def get_users(user_ids: list[int]) -> list[User]:
    users_in_group: AsyncGenerator[ChatMember, None] = tg_app.get_chat_members(GROUP_ID)
    return [x.user async for x in users_in_group if x.user.id in user_ids]
