from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared

whitelistbp = Blueprint("whitelist")


@whitelistbp.get("/whitelist")
@openapi.response(200, '{"whitelist": [<whitelist>], "defwhitelist": [<defwhitelist>]}')
async def get_whitelist(req: Request):
    return json({"whitelist": shared.whitelist, "defwhitelist": shared.DEF_WHITELIST})


@whitelistbp.post("/whitelist")
@openapi.response(200, '{"currwhitelist": [<currwhitelist>], "defwhitelist": [<defwhitelist>]}')
async def add_to_whitelist(req: Request):
    id_to_add = int(req.args.get("id", 0))
    if id_to_add not in shared.whitelist:
        shared.whitelist.append(id_to_add)
    return json({"currwhitelist": shared.whitelist, "defwhitelist": shared.DEF_WHITELIST})
