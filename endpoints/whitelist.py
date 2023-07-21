from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from ext.auth_check import auth_check

whitelistbp = Blueprint("whitelist")


@whitelistbp.get("/whitelist")
@openapi.parameter("Authorization", location="header")
@auth_check
@openapi.response(200, '{"whitelist": [<whitelist>]}')
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
async def get_whitelist(req: Request):
    return json({"whitelist": shared.whitelist})


@whitelistbp.post("/whitelist")
@openapi.parameter("Authorization", location="header")
@auth_check
@openapi.response(200, '{"currwhitelist": [<currwhitelist>]}')
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.parameter("id", int)
async def add_to_whitelist(req: Request):
    id_to_add = int(req.args.get("id", 0))
    if id_to_add not in shared.whitelist and id_to_add != 0:
        shared.whitelist.append(id_to_add)
    return json({"currwhitelist": shared.whitelist})
