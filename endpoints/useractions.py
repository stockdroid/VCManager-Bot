from pyrogram.raw.functions.phone import EditGroupCallParticipant
from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from shared import call_py, tg_app

useractionsbp = Blueprint("useractionsbp")


@useractionsbp.get("/mute/<id_user:int>")
@openapi.response(200, '{"muted": True}')
async def mute_user(req: Request, id_user: int):
    voice_chat = await call_py._app.get_full_chat(shared.GROUP_ID)
    await tg_app.invoke(
        EditGroupCallParticipant(
            call=voice_chat,
            participant=await call_py._app.resolve_peer(id_user),
            muted=True
        )
    )
    return json({"muted": True})


@useractionsbp.get("/allow/<id_user:int>")
@openapi.response(200, '{"unmuted": True}')
async def unmute_user(req: Request, id_user: int):
    voice_chat = await call_py._app.get_full_chat(shared.GROUP_ID)
    await tg_app.invoke(
        EditGroupCallParticipant(
            call=voice_chat,
            participant=await call_py._app.resolve_peer(id_user),
            muted=False
        )
    )
    return json({"unmuted": True})


@useractionsbp.post("/volume/<id_user:int>")
@openapi.response(200, '{"volume": <vol>}')
async def set_queue_index(req: Request, id_user: int):
    voice_chat = await call_py._app.get_full_chat(shared.GROUP_ID)
    await tg_app.invoke(
        EditGroupCallParticipant(
            call=voice_chat,
            participant=await call_py._app.resolve_peer(id_user),
            volume=int(req.args.get("volume", 100))
        )
    )
    return json({"volume": int(req.args.get("volume", 100))})
