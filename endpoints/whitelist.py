from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared

whitelistbp = Blueprint("whitelist")


@whitelistbp.get("/whitelist")
@openapi.response(200, '{"whitelist": [<whitelist>]}')
async def get_whitelist(req: Request):
    return json({"whitelist": shared.whitelist})


@whitelistbp.post("/whitelist")
@openapi.response(200, '{"currwhitelist": [<currwhitelist>]}')
@openapi.parameter("id", int)
async def add_to_whitelist(req: Request):
    id_to_add = int(req.args.get("id", 0))
    if id_to_add not in shared.whitelist and id_to_add != 0:
        shared.whitelist.append(id_to_add)
    return json({"currwhitelist": shared.whitelist})
