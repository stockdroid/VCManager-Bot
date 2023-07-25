from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from ext.auth_check import auth_check
from ext.log_helper import request_log
import json as jsonlib
limitsbp = Blueprint("limits")


@limitsbp.get("/limits")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"currlimit": 3, "deflimit": 2}})
@openapi.summary("Get people limit")
@openapi.description("Gets the max number of unmuted people in the voice chat")
@openapi.secured("token")
@auth_check
async def getLimits(req: Request):
    await request_log(req, True, jsonlib.dumps({"currlimit": shared.limit, "deflimit": shared.DEF_LIMIT}), "")
    return json({"currlimit": shared.limit, "deflimit": shared.DEF_LIMIT})


@limitsbp.post("/limits")
@openapi.secured("token")
@openapi.parameter("limit", int)
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"currlimit": 4, "exlimit": 3, "deflimit": 2}})
@auth_check
async def setLimits(req: Request):
    limit = int(req.args.get("limit", shared.limit))
    ex_limit = shared.limit
    shared.limit = limit
    await request_log(req, True, jsonlib.dumps({"currlimit": shared.limit, "exlimit": ex_limit, "deflimit": shared.DEF_LIMIT}), "")
    return json({"currlimit": shared.limit, "exlimit": ex_limit, "deflimit": shared.DEF_LIMIT})
