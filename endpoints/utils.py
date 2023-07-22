import base64
import json as jsonlib

from pyrogram.errors import PeerIdInvalid
from pyrogram.raw.functions.phone import GetGroupParticipants
from pyrogram.types import Photo
from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from ext.auth_check import auth_check
from ext.log_helper import request_log
from shared import call_py, tg_app

utilsbp = Blueprint("utils")


@utilsbp.get("/devmode")
@openapi.secured("token")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"devmode": <status>}')
async def is_devmode(req: Request):
    await request_log(req, True, jsonlib.dumps({"devmode": shared.DEV_MODE}), "")
    return json({"devmode": shared.DEV_MODE})


@utilsbp.get("/commands")
@openapi.secured("token")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"commands_enabled": <status>}')
async def commands_enabled(req: Request):
    await request_log(req, True, jsonlib.dumps({"commands_enabled": shared.COMMANDS_ENABLED}), "")
    return json({"commands_enabled": shared.COMMANDS_ENABLED})


@utilsbp.get("/groupid")
@openapi.secured("token")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"groupid": <groupid>}')
async def groupid(req: Request):
    await request_log(req, True, jsonlib.dumps({"groupid": shared.GROUP_ID}), "")
    return json({"groupid": shared.GROUP_ID})


@utilsbp.get("/resolve/<username:str>")
@openapi.secured("token")
@auth_check
@openapi.response(200, '{"username": <username>, "id": <id>}')
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(422, '{"error": "PEER_ID_INVALID"}')
async def resolve(req: Request, username: str):
    try:
        user_id = await tg_app.resolve_peer(username)
        await request_log(req, True, jsonlib.dumps({"username": username, "id": user_id.user_id}), "")
        return json({"username": username, "id": user_id.user_id})
    except PeerIdInvalid:
        await request_log(req, False, "", jsonlib.dumps({"error": "PEER_ID_INVALID"}))
        return json({"error": "PEER_ID_INVALID"}, 422)


@utilsbp.get("/info/<user_id:int>")
@openapi.secured("token")
@auth_check
@openapi.response(200, '{"user_id": <id>, "info": {<info>}}')
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(422, '{"error": "PEER_ID_INVALID"}')
async def info(req: Request, user_id: int):
    try:
        user_info = await tg_app.get_users(user_id)
        await request_log(req, True, jsonlib.dumps({"user_id": user_id, "info": jsonlib.loads(str(user_info))}), "")
        return json({"user_id": user_id, "info": jsonlib.loads(str(user_info))})
    except:
        await request_log(req, False, "", jsonlib.dumps({"error": "PEER_ID_INVALID"}))
        return json({"error": "PEER_ID_INVALID"}, 422)


@utilsbp.get("/participants")
@openapi.secured("token")
@auth_check
@openapi.response(200, '{"participants": [<participants>]}')
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(422, '{"error": "NOT_IN_VOICECHAT"}')
async def participants(req: Request):
    if call_py.full_chat is None or call_py.full_chat.call is None:
        await request_log(req, False, "", jsonlib.dumps({"error": "NOT_IN_VOICECHAT"}))
        return json({"error": "NOT_IN_VOICECHAT"}, 422)
    else:
        participants_list = (await tg_app.invoke(GetGroupParticipants(
            call=call_py.full_chat.call, ids=[], sources=[], offset="", limit=-1
        ))).participants
        await request_log(req, True, jsonlib.dumps({"participants": jsonlib.loads(str(participants_list))}), "")
        return json({"participants": jsonlib.loads(str(participants_list))})


@utilsbp.get("/pfp/<user_id:int>")
@openapi.secured("token")
@auth_check
@openapi.response(200, '{"user_id": <id>, "media": <base64jpeg>}')
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(422, '{"error": "PEER_ID_INVALID"}')
async def pfp(req: Request, user_id: int):
    try:
        photos = tg_app.get_chat_photos(user_id, 1)
        photo: Photo
        async for photoelem in photos:
            photo = photoelem
        media = await tg_app.download_media(photo.file_id, in_memory=True)
        await request_log(req, True, jsonlib.dumps({
                "user_id": user_id,
                "media": "data:image/jpeg;base64," + base64.b64encode(media.getvalue()).decode("UTF-8")
            }), "")
        return json(
            {
                "user_id": user_id,
                "media": "data:image/jpeg;base64," + base64.b64encode(media.getvalue()).decode("UTF-8")
            }
        )
    except PeerIdInvalid:
        await request_log(req, False, "", jsonlib.dumps({"error": "PEER_ID_INVALID"}))
        return json({"error": "PEER_ID_INVALID"}, 422)
