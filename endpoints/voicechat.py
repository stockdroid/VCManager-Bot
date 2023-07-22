import math
import random

from pyrogram.raw.functions.phone import DiscardGroupCall, CreateGroupCall, EditGroupCallTitle, ToggleGroupCallRecord
from sanic import Blueprint, json, Request
from sanic_ext.extensions.openapi import openapi

import shared
from ext.auth_check import auth_check
from ext.log_helper import request_log
from shared import call_py, tg_app
import json as jsonlib

voicechatbp = Blueprint("voicechat")


@voicechatbp.post("/voicechat/end")
@openapi.secured("token")
@auth_check
@openapi.response(200, '{"ended": true}')
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(204, '{"error": "NoVC"}')
async def end_vc(req: Request):
    try:
        await tg_app.invoke(DiscardGroupCall(call=call_py.full_chat.call))
        await request_log(req, True, jsonlib.dumps({"ended": True}), "")
        return json({"ended": True})
    except:
        await request_log(req, False, "", jsonlib.dumps({"error": "NoVC"}))
        return json({"error": "NoVC"}, 204)


@voicechatbp.post("/voicechat/create")
@openapi.secured("token")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"created": <state>}')
async def create_vc(req: Request):
    try:
        await tg_app.invoke(CreateGroupCall(peer=await tg_app.resolve_peer(shared.GROUP_ID),
                                            random_id=int((random.random() * 1000) * (random.random() * 1000))))
        await call_py.start(shared.GROUP_ID)
        await request_log(req, True, jsonlib.dumps({"created": True}), "")
        return json({"created": True})
    except:
        await request_log(req, False, "", jsonlib.dumps({"created": False}))
        return json({"created": False})


@voicechatbp.post("/voicechat/status")
@openapi.secured("token")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"vcpresent": <state>}')
async def status_vc(req: Request):
    await request_log(req, True, jsonlib.dumps({"vcpresent": call_py.full_chat is not None}), "")
    return json({"vcpresent": call_py.full_chat is not None})


@voicechatbp.post("/voicechat/title")
@openapi.secured("token")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"newtitle": <title>}')
@openapi.parameter("title", str)
async def change_title(req: Request):
    new_title = req.args.get("title", "")
    await tg_app.invoke(EditGroupCallTitle(call=call_py.full_chat.call, title=new_title))
    await request_log(req, True, jsonlib.dumps({"newtitle": new_title}), "")
    return json({"newtitle": new_title})


@voicechatbp.post("/voicechat/record")
@openapi.secured("token")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"record": <state>}')
@openapi.parameter("start", bool)
@openapi.parameter("video", bool)
async def record_vc(req: Request):
    start = req.args.get("start", False) == "true"
    video = req.args.get("video", True) == "true"
    await tg_app.invoke(
        ToggleGroupCallRecord(call=call_py.full_chat.call, start=start, video=video, video_portrait=False))
    await request_log(req, True, jsonlib.dumps({"record": start}), "")
    return json({"record": start})


@voicechatbp.post("/voicechat/join")
@openapi.secured("token")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"joined": true}')
async def join_vc(req: Request):
    await call_py.start(shared.GROUP_ID)
    await request_log(req, True, jsonlib.dumps({"joined": shared.whitelist}), "")
    return json({"joined": True})
