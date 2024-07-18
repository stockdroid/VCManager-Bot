import asyncio
from sanic import Blueprint, Request, json
from sanic_ext import openapi

import shared
from ext.auth_check import auth_check
import json as jsonlib

from ext.log_helper import request_log
from ext.queue_json_encoder import CustomJSONEncoder
from pyrogram.raw.types import InputPeerUser

queuebp = Blueprint("queue")

@queuebp.get("/queue")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"queue": [777000, 123456]}})
@auth_check
async def get_queue(req: Request):
    asyncio.create_task(request_log(req, True, jsonlib.dumps({"queue": shared.muted_queue}, cls=CustomJSONEncoder), ""))
    return json({"queue": shared.muted_queue}, cls=CustomJSONEncoder)

@queuebp.get("/queue/<id_user:int>")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"queuepos": 2}})
@auth_check
async def get_queue_index(req: Request, id_user: int):
    try:
        queue_index = next((i for i, user in enumerate(shared.muted_queue) if user.user_id == id_user), None)
    except ValueError:
        queue_index = None
    asyncio.create_task(request_log(req, True, jsonlib.dumps({"queuepos": queue_index}, cls=CustomJSONEncoder), ""))
    return json({"queuepos": queue_index}, cls=CustomJSONEncoder)

@queuebp.post("/queue/<id_user:int>")
@openapi.secured("token")
@openapi.parameter("index", int)
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"queuepos": 4}})
@auth_check
async def set_queue_index(req: Request, id_user: int):
    try:
        user_to_move = next(user for user in shared.muted_queue if user.user_id == id_user)
    except StopIteration:
        return json({"error": "User not found in queue"}, status=404)

    current_index = shared.muted_queue.index(user_to_move)
    new_index = int(req.args.get("index", current_index))

    if new_index < 0 or new_index >= len(shared.muted_queue):
        return json({"error": "Invalid index"}, status=400)

    shared.muted_queue.insert(new_index, shared.muted_queue.pop(current_index))
    asyncio.create_task(request_log(req, True, jsonlib.dumps({"queuepos": new_index}, cls=CustomJSONEncoder), ""))
    return json({"queuepos": new_index}, cls=CustomJSONEncoder)
