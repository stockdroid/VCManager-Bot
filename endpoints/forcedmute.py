from sanic import Blueprint, Request, json
from sanic_ext import openapi

import shared
from ext.auth_check import auth_check

forcedmutesbp = Blueprint("forcedmutes")


@forcedmutesbp.get("/forcedmutes")
@auth_check
@openapi.response(200, '{"forcedmutes": [<ids>]}')
async def get_forcedmutes(req: Request):
    return json({"forcedmutes": shared.force_muted})

@forcedmutesbp.post("/forcedmutes/<id_user:int>")
@auth_check
@openapi.response(200, '{"inforcedmutes": <bool>}')
async def get_in_forcedmutes(req: Request, id_user: int):
    return json({"inforcedmutes": id_user in shared.force_muted})

@forcedmutesbp.post("/forcedmutes/action/<id_user:int>")
@auth_check
@openapi.parameter("action", str)
@openapi.description("action can be either add or remove")
@openapi.response(200, '{"action": <action>, "done": <state>}')
@openapi.response(204, '{"error": "UnrecognizedAction"}')
async def action_forcedmutes(req: Request, id_user: int):
    done = False
    if req.args.get("action", "") not in ["add", "remove"]:
        return json({"error": "UnrecognizedAction"}, 204)
    else:
        if req.args.get("action", "") == "add":
            if id_user not in shared.force_muted:
                done = True
                shared.force_muted.append(id_user)
        else:
            if id_user not in shared.force_muted:
                done = True
                shared.force_muted.remove(id_user)
        return json({"action": req.args.get("action", ""), "done": done})

