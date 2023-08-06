import asyncio

from sanic import Blueprint, Request, json
from sanic_ext import openapi

import shared
from ext.auth_check import auth_check
import json as jsonlib

from ext.log_helper import request_log

queuebp = Blueprint("queue")


@queuebp.get("/queue")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"queue": [777000, 123456]}})
@auth_check
async def get_queue(req: Request):
    asyncio.create_task(request_log(req, True, jsonlib.dumps({"queue": shared.muted_queue}), ""))
    return json({"queue": shared.muted_queue})


@queuebp.get("/queue/<id_user:int>")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"queuepos": 2}})
@auth_check
async def get_queue_index(req: Request, id_user: int):
    try:
        queue_index = shared.muted_queue.index(id_user)
    except ValueError:
        queue_index = None
    asyncio.create_task(request_log(req, True, jsonlib.dumps({"queuepos": queue_index}), ""))
    return json({"queuepos": queue_index})


@queuebp.post("/queue/<id_user:int>")
@openapi.secured("token")
@openapi.parameter("index", int)
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"queuepos": 4}})
@auth_check
async def set_queue_index(req: Request, id_user: int):
    new_index = int(req.args.get("index", shared.muted_queue.index(id_user)))
    shared.muted_queue.remove(id_user)
    shared.muted_queue.insert(new_index, id_user)
    asyncio.create_task(request_log(req, True, jsonlib.dumps({"queuepos": new_index}), ""))
    return json({"queuepos": new_index})
