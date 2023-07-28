import base64
import json as jsonlib
from typing import List, AsyncGenerator

from pyrogram.errors import PeerIdInvalid
from pyrogram.raw.functions.phone import GetGroupParticipants
from pyrogram.types import Photo, User, ChatMember
from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from ext.auth_check import auth_check
from ext.get_user import get_user, get_users
from ext.log_helper import request_log
from shared import call_py, tg_app

utilsbp = Blueprint("utils")


@utilsbp.get("/devmode")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"devmode": True}})
@auth_check
async def is_devmode(req: Request):
    await request_log(req, True, jsonlib.dumps({"devmode": shared.DEV_MODE}), "")
    return json({"devmode": shared.DEV_MODE})


@utilsbp.get("/commands")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"commands_enabled": False}})
@auth_check
async def commands_enabled(req: Request):
    await request_log(req, True, jsonlib.dumps({"commands_enabled": shared.COMMANDS_ENABLED}), "")
    return json({"commands_enabled": shared.COMMANDS_ENABLED})


@utilsbp.get("/groupid")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"groupid": -100123456}})
@auth_check
async def groupid(req: Request):
    await request_log(req, True, jsonlib.dumps({"groupid": shared.GROUP_ID}), "")
    return json({"groupid": shared.GROUP_ID})


@utilsbp.get("/resolve/<username:str>")
@openapi.secured("token")
@openapi.response(200, {"application/json": {"username": "chicchi7393", "id": 704625262}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(422, {"application/json": {"error": "PEER_ID_INVALID"}})
@auth_check
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
@openapi.response(200, {"application/json": {"user_id": 704625262, "info": {"user_id": 704625262}}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(422, {"application/json": {"error": "PEER_ID_INVALID"}})
@auth_check
async def info(req: Request, user_id: int):
    user = await get_user(user_id)
    await request_log(req, True, jsonlib.dumps(user), "")
    return json({"user_id": user.id, "info": jsonlib.loads(str(user))})


@utilsbp.get("/massinfo/<user_ids:str>")
@openapi.description(text="Separare gli user id da una virgola, prendere solo utenti nel gruppo")
@openapi.secured("token")
@openapi.response(200, {"application/json": [{"user_id": 704625262, "info": {"user_id": 704625262}}]})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@auth_check
async def massinfo(req: Request, user_ids: str):
    users = await get_users([int(x) for x in user_ids.split("%2C") if x.isdigit()])
    list_info = [{"user_id": x.id, "info": jsonlib.loads(str(x))} for x in users]
    await request_log(req, True, jsonlib.dumps(list_info), "")
    return json(list_info)


@utilsbp.get("/participants")
@openapi.secured("token")
@openapi.response(200, {"application/json": {"participants": [70462562, 777000]}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(422, {"application/json": {"error": "NOT_IN_VOICECHAT"}})
@auth_check
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
@openapi.response(200, {"application/json": {"user_id": 70462562, "media": "data:image/jpeg;base64,..."}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(422, {"application/json": {"error": "PEER_ID_INVALID"}})
@auth_check
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


@utilsbp.get("/gworkspace/roles")
@openapi.secured("token")
@openapi.response(200, {"application/json": {"roles": []}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(401, {"application/json": {"error": "NO_CF_ACCESS"}})
@auth_check
async def get_user_roles(req: Request):
    if not shared.ENABLE_CF_AUTH:
        await request_log(req, False, "", jsonlib.dumps({"error": "NO_CF_ACCESS"}))
        return json({"error": "NO_CF_ACCESS"}, 401)
    else:
        await request_log(req, True, jsonlib.dumps({"roles": req.ctx.groups}), "")
        return json({"roles": req.ctx.groups})


@utilsbp.get("/gworkspace/name")
@openapi.secured("token")
@openapi.response(200, {"application/json": {"name": "realname"}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(401, {"application/json": {"error": "NO_CF_ACCESS"}})
@auth_check
async def get_user_name(req: Request):
    if not shared.ENABLE_CF_AUTH:
        await request_log(req, False, "", jsonlib.dumps({"error": "NO_CF_ACCESS"}))
        return json({"error": "NO_CF_ACCESS"}, 401)
    else:
        await request_log(req, True, jsonlib.dumps({"name": req.ctx.name}), "")
        return json({"name": req.ctx.name})
