from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from ext.auth_check import auth_check

limitsbp = Blueprint("limits")


@limitsbp.get("/limits")
@auth_check
@openapi.response(200, '{"currlimit": <limit>, "deflimit": <deflimit>}')
async def getLimits(req: Request):
    return json({"currlimit": shared.limit, "deflimit": shared.DEF_LIMIT})


@limitsbp.post("/limits")
@auth_check
@openapi.parameter("limit", int)
@openapi.response(200, '{"currlimit": <limit>, "exlimit": <exlimit>, "deflimit": <deflimit>}')
async def setLimits(req: Request):
    limit = int(req.args.get("limit", shared.limit))
    ex_limit = shared.limit
    shared.limit = limit
    return json({"currlimit": shared.limit, "exlimit": ex_limit, "deflimit": shared.DEF_LIMIT})
