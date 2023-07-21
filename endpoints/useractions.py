from pyrogram.errors import PeerIdInvalid
from pyrogram.raw.functions.phone import EditGroupCallParticipant
from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from ext.auth_check import auth_check
from shared import call_py, tg_app

useractionsbp = Blueprint("useractionsbp")


@useractionsbp.post("/mute/<id_user:int>")
@openapi.secured("token")
@auth_check
@openapi.response(200, '{"muted": True}')
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(422, '{"error": "PEER_ID_INVALID"}')
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
        return json({"muted": True})
    except PeerIdInvalid:
        return json({"error": "PEER_ID_INVALID"}, 422)


@useractionsbp.post("/allow/<id_user:int>")
@openapi.secured("token")
@auth_check
@openapi.response(200, '{"unmuted": True}')
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(422, '{"error": "PEER_ID_INVALID"}')
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
        return json({"muted": False})
    except PeerIdInvalid:
        return json({"error": "PEER_ID_INVALID"}, 422)


@useractionsbp.post("/volume/<id_user:int>")
@openapi.secured("token")
@auth_check
@openapi.response(200, '{"volume": <vol>}')
@openapi.parameter('volume', int)
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(422, '{"error": "PEER_ID_INVALID"}')
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
        return json({"volume": int(req.args.get("volume", 100))})
    except PeerIdInvalid:
        return json({"error": "PEER_ID_INVALID"}, 422)
