import asyncio

from pyrogram.errors import PeerIdInvalid
from pyrogram.raw.functions.phone import EditGroupCallParticipant
from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from ext.auth_check import auth_check
from ext.get_user import get_user
from ext.log_helper import request_log
from shared import call_py, tg_app
import json as jsonlib

useractionsbp = Blueprint("useractionsbp")


@useractionsbp.post("/mute/<id_user:int>")
@openapi.secured("token")
@openapi.response(200, {"application/json": {"muted": True}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(422, {"application/json": {"error": "PEER_ID_INVALID"}})
@auth_check
async def mute_user(req: Request, id_user: int):
    voice_chat = call_py.full_chat.call
    try:
        await tg_app.invoke(
            EditGroupCallParticipant(
                call=voice_chat,
                participant=await tg_app.resolve_peer(id_user),
                muted=True
            )
        )
        if id_user not in shared.force_muted:
            shared.force_muted.append(id_user)
        asyncio.create_task(request_log(req, True, jsonlib.dumps({"muted": True}), ""))
        return json({"muted": True})
    except PeerIdInvalid:
        asyncio.create_task(request_log(req, False, "", jsonlib.dumps({"error": "PEER_ID_INVALID"})))
        return json({"error": "PEER_ID_INVALID"}, 422)


@useractionsbp.post("/allow/<id_user:int>")
@openapi.secured("token")
@openapi.response(200, {"application/json": {"unmuted": True}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(422, {"application/json": {"error": "PEER_ID_INVALID"}})
@auth_check
async def unmute_user(req: Request, id_user: int):
    voice_chat = call_py.full_chat.call
    try:
        await tg_app.invoke(
            EditGroupCallParticipant(
                call=voice_chat,
                participant=await tg_app.resolve_peer(id_user),
                muted=False
            )
        )
        if id_user in shared.force_muted:
            shared.force_muted.remove(id_user)
        asyncio.create_task(request_log(req, True, jsonlib.dumps({"muted": False}), ""))
        return json({"muted": False})
    except PeerIdInvalid:
        asyncio.create_task(request_log(req, False, "", jsonlib.dumps({"error": "PEER_ID_INVALID"})))
        return json({"error": "PEER_ID_INVALID"}, 422)


@useractionsbp.post("/volume/<id_user:int>")
@openapi.secured("token")
@openapi.parameter('volume', int)
@openapi.response(200, {"application/json": {"volume": 100}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(422, {"application/json": {"error": "PEER_ID_INVALID"}})
@auth_check
async def set_volume(req: Request, id_user: int):
    voice_chat = call_py.full_chat.call
    try:
        await tg_app.invoke(
            EditGroupCallParticipant(
                call=voice_chat,
                participant=await tg_app.resolve_peer(id_user),
                volume=int(req.args.get("volume", 100))
            )
        )
        asyncio.create_task(request_log(req, True, jsonlib.dumps({"volume": int(req.args.get("volume", 100))}), ""))
        return json({"volume": int(req.args.get("volume", 100))})
    except PeerIdInvalid:
        asyncio.create_task(request_log(req, False, "", jsonlib.dumps({"error": "PEER_ID_INVALID"})))
        return json({"error": "PEER_ID_INVALID"}, 422)
