import math
import random

from pyrogram.errors import BadRequest
from pyrogram.raw.types.messages import ChatFull
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat
from pyrogram.raw.functions.phone import DiscardGroupCall, CreateGroupCall, EditGroupCallTitle, ToggleGroupCallRecord, \
    GetGroupCall
from pyrogram.raw.types.phone import GroupCall
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
@openapi.response(200, {"application/json": {"ended": True}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(400, {"application/json": {"error": "NoVC"}})
@auth_check
async def end_vc(req: Request):
    try:
        await tg_app.invoke(DiscardGroupCall(call=call_py.full_chat.call))
        await request_log(req, True, jsonlib.dumps({"ended": True}), "")
        return json({"ended": True})
    except:
        await request_log(req, False, "", jsonlib.dumps({"error": "NoVC"}))
        return json({"error": "NoVC"}, 400)


@voicechatbp.post("/voicechat/create")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"created": True}})
@auth_check
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


@voicechatbp.get("/voicechat/invc")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"vcpresent": False}})
@auth_check
async def invc_vc(req: Request):
    await request_log(req, True, jsonlib.dumps({"vcpresent": call_py.group_call is not None}), "")
    return json({"vcpresent": call_py.full_chat is not None})


@voicechatbp.get("/voicechat/exists")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"vcpresent": False}})
@auth_check
async def exists_vc(req: Request):
    chat: ChatFull = await tg_app.invoke(GetFullChannel(channel=await tg_app.resolve_peer(shared.GROUP_ID)))
    await request_log(req, True, jsonlib.dumps({"vcpresent": chat.full_chat.call is not None}), "")
    return json({"vcpresent": call_py.full_chat is not None})


@voicechatbp.post("/voicechat/title")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"newtitle": "Test response"}})
@openapi.parameter("title", str)
@auth_check
async def change_title(req: Request):
    new_title = req.args.get("title", "")
    await tg_app.invoke(EditGroupCallTitle(call=call_py.full_chat.call, title=new_title))
    await request_log(req, True, jsonlib.dumps({"newtitle": new_title}), "")
    return json({"newtitle": new_title})


@voicechatbp.post("/voicechat/record")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(400, {"application/json": {"error": "GROUPCALL_NOT_MODIFIED"}})
@openapi.response(200, {"application/json": {"record": True}})
@openapi.parameter("start", bool)
@openapi.parameter("video", bool)
@auth_check
async def record_vc(req: Request):
    try:
        start = req.args.get("start", False) == "true"
        video = req.args.get("video", True) == "true"
        await tg_app.invoke(
            ToggleGroupCallRecord(call=call_py.full_chat.call, start=start, video=video, video_portrait=False))
        await request_log(req, True, jsonlib.dumps({"record": start}), "")
        return json({"record": start})
    except BadRequest as e:
        await request_log(req, False, "", jsonlib.dumps({"error": "GROUPCALL_NOT_MODIFIED"}))
        return json({"error": "GROUPCALL_NOT_MODIFIED"}, 400)


@voicechatbp.post("/voicechat/info")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(400, {"application/json": {"error": "GROUPCALL_NOT_EXIST"}})
@openapi.response(200, {"application/json": {"info": {}}})
@auth_check
async def info_vc(req: Request):
    chat: ChatFull = await tg_app.invoke(GetFullChannel(channel=await tg_app.resolve_peer(shared.GROUP_ID)))
    if chat.full_chat.call is None:
        await request_log(req, False, "", jsonlib.dumps({"error": "GROUPCALL_NOT_EXIST"}))
        return json({"error": "GROUPCALL_NOT_EXIST"}, 400)
    else:
        group_call: GroupCall = await tg_app.invoke(GetGroupCall(call=chat.full_chat.call, limit=1))
        await request_log(req, True, jsonlib.dumps({"info": jsonlib.loads(str(group_call.call))}), "")
        return json({"info": jsonlib.loads(str(group_call.call))})


@voicechatbp.post("/voicechat/join")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"joined": True}})
@auth_check
async def join_vc(req: Request):
    await call_py.start(shared.GROUP_ID)
    await request_log(req, True, jsonlib.dumps({"joined": shared.whitelist}), "")
    return json({"joined": True})
