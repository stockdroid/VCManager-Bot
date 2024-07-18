import asyncio

from sanic import Blueprint, Request, json
from sanic_ext import openapi

import shared
from shared import tg_app, call_py
from ext.auth_check import auth_check
from ext.log_helper import request_log
import json as jsonlib

from pyrogram.raw.functions.phone import EditGroupCallParticipant
from pyrogram.raw.types import InputGroupCall

forcedmutesbp = Blueprint("forcedmutes")


@forcedmutesbp.get("/forcedmutes")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"forcedmutes": [777000, 12345]}})
@auth_check
async def get_forcedmutes(req: Request):
    asyncio.create_task(request_log(req, True, jsonlib.dumps({"forcedmutes": shared.force_muted}), ""))
    return json({"forcedmutes": shared.force_muted})


@forcedmutesbp.post("/forcedmutes/<id_user:int>")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"inforcedmutes": True}})
@auth_check
async def get_in_forcedmutes(req: Request, id_user: int):
    asyncio.create_task(request_log(req, True, jsonlib.dumps({"inforcedmutes": id_user in shared.force_muted}), ""))
    return json({"inforcedmutes": id_user in shared.force_muted})


@forcedmutesbp.post("/forcedmutes/action/<id_user:int>")
@openapi.secured("token")
@openapi.parameter("action", str)
@openapi.description("action can be either add or remove")
@openapi.response(200, {"application/json": {"action": "add", "done": True}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(400, {"application/json": {"error": "UnrecognizedAction"}})
@auth_check
async def action_forcedmutes(req: Request, id_user: int):
    done = False
    if req.args.get("action", "") not in ["add", "remove"]:
        asyncio.create_task(request_log(req, False, "", jsonlib.dumps({"error": "UnrecognizedAction"})))
        return json({"error": "UnrecognizedAction"}, 400)
    else:
        if req.args.get("action", "") == "add":
            if id_user not in shared.force_muted and id_user not in shared.whitelist:
                done = True
                group_call: InputGroupCall = call_py.full_chat.call
                await tg_app.invoke(EditGroupCallParticipant(
                call=group_call,
                participant=await tg_app.resolve_peer(id_user),
                muted=True
            ))
                shared.force_muted.append(id_user)
        else:
            if id_user in shared.force_muted and id_user not in shared.whitelist:
                done = True
                group_call: InputGroupCall = call_py.full_chat.call
                await tg_app.invoke(EditGroupCallParticipant(
                call=group_call,
                participant=await tg_app.resolve_peer(id_user),
                muted=False
            ))
                shared.force_muted.remove(id_user)
        asyncio.create_task(request_log(req, True, jsonlib.dumps({"action": req.args.get("action", ""), "done": done}), ""))
        return json({"action": req.args.get("action", ""), "done": done})
