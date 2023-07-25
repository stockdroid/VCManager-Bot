from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from ext.auth_check import auth_check
from ext.log_helper import request_log
import json as jsonlib

whitelistbp = Blueprint("whitelist")


@whitelistbp.get("/whitelist")
@openapi.secured("token")
@openapi.response(200, {"application/json": {"whitelist": []}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@auth_check
async def get_whitelist(req: Request):
    await request_log(req, True, jsonlib.dumps({"whitelist": shared.whitelist}), "")
    return json({"whitelist": shared.whitelist})


@whitelistbp.put("/whitelist")
@openapi.secured("token")
@openapi.response(200, {"application/json": {"currwhitelist": []}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.parameter("id", int)
@auth_check
async def add_to_whitelist(req: Request):
    id_to_add = int(req.args.get("id", 0))
    if id_to_add not in shared.whitelist and id_to_add != 0:
        shared.whitelist.append(id_to_add)
    await request_log(req, True, jsonlib.dumps({"currwhitelist": shared.whitelist}), "")
    return json({"currwhitelist": shared.whitelist})


@whitelistbp.delete("/whitelist")
@openapi.secured("token")
@openapi.response(200, {"application/json": {"currwhitelist": []}})
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.parameter("id", int)
@auth_check
async def remove_to_whitelist(req: Request):
    id_to_add = int(req.args.get("id", 0))
    if id_to_add in shared.whitelist and id_to_add != 0:
        shared.whitelist.remove(id_to_add)
    await request_log(req, True, jsonlib.dumps({"currwhitelist": shared.whitelist}), "")
    return json({"currwhitelist": shared.whitelist})
