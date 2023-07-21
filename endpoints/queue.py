from sanic import Blueprint, Request, json
from sanic_ext import openapi

import shared
from ext.auth_check import auth_check

queuebp = Blueprint("queue")


@queuebp.get("/queue")
@openapi.secured("token")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"queue": [<ids>]}')
async def get_queue(req: Request):
    return json({"queue": shared.muted_queue})


@queuebp.get("/queue/<id_user:int>")
@openapi.secured("token")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"queuepos": <pos>}')
async def get_queue_index(req: Request, id_user: int):
    try:
        queue_index = shared.muted_queue.index(id_user)
    except ValueError:
        queue_index = None
    return json({"queuepos": queue_index})


@queuebp.post("/queue/<id_user:int>")
@openapi.secured("token")
@auth_check
@openapi.parameter("index", int)
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"queuepos": <pos>}')
async def set_queue_index(req: Request, id_user: int):
    new_index = int(req.args.get("index", shared.muted_queue.index(id_user)))
    shared.muted_queue.remove(id_user)
    shared.muted_queue.insert(new_index, id_user)
    return json({"queuepos": new_index})
