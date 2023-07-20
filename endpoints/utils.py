import base64
import json as jsonlib

from pyrogram.errors import PeerIdInvalid
from pyrogram.raw.functions.phone import GetGroupParticipants
from pyrogram.types import Photo
from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from shared import call_py, tg_app

utilsbp = Blueprint("utils")


@utilsbp.get("/devmode")
@openapi.response(200, '{"devmode": <status>}')
async def is_devmode(req: Request):
    return json({"devmode": shared.DEV_MODE})


@utilsbp.get("/commands")
@openapi.response(200, '{"commands_enabled": <status>}')
async def commands_enabled(req: Request):
    return json({"commands_enabled": shared.COMMANDS_ENABLED})


@utilsbp.get("/groupid")
@openapi.response(200, '{"groupid": <groupid>}')
async def groupid(req: Request):
    return json({"groupid": shared.GROUP_ID})


@utilsbp.get("/resolve/<username:str>")
@openapi.response(200, '{"username": <username>, "id": <id>}')
@openapi.response(422, '{"error": "PEER_ID_INVALID"}')
async def resolve(req: Request, username: str):
    try:
        user_id = await tg_app.resolve_peer(username)
        return json({"username": username, "id": user_id.user_id})
    except PeerIdInvalid:
        return json({"error": "PEER_ID_INVALID"}, 422)


@utilsbp.get("/info/<user_id:int>")
@openapi.response(200, '{"user_id": <id>, "info": {<info>}}')
@openapi.response(422, '{"error": "PEER_ID_INVALID"}')
async def info(req: Request, user_id: int):
    try:
        user_info = await tg_app.get_users(user_id)
        return json({"user_id": user_id, "info": jsonlib.loads(str(user_info))})
    except:
        return json({"error": "PEER_ID_INVALID"}, 422)



@utilsbp.get("/participants")
@openapi.response(200, '{"participants": [<participants>]}')
@openapi.response(422, '{"error": "NOT_IN_VOICECHAT"}')
async def participants(req: Request):
    if call_py.full_chat.call is None:
        return json({"error": "NOT_IN_VOICECHAT"}, 422)
    else:
        participants_list = (await tg_app.invoke(GetGroupParticipants(
            call = call_py.full_chat.call, ids = [], sources = [], offset = "", limit=-1
        ))).participants
        return json({"participants": jsonlib.loads(str(participants_list))})


@utilsbp.get("/pfp/<user_id:int>")
@openapi.response(200, '{"user_id": <id>, "media": <base64jpeg>}')
@openapi.response(422, '{"error": "PEER_ID_INVALID"}')
async def pfp(req: Request, user_id: int):
    try:
        photos = tg_app.get_chat_photos(user_id, 1)
        photo: Photo
        async for photoelem in photos:
            photo = photoelem
        media = await tg_app.download_media(photo.file_id, in_memory=True)
        return json(
            {
                "user_id": user_id,
                "media": "data:image/jpeg;base64," + base64.b64encode(media.getvalue()).decode("UTF-8")
            }
        )
    except PeerIdInvalid:
        return json({"error": "PEER_ID_INVALID"}, 422)

