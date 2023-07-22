from sanic import Blueprint, Request, text
from sanic_ext.extensions.openapi import openapi

from ext.auth_check import auth_check
from ext.log_helper import request_log

rootBp = Blueprint("root")


@rootBp.get("/")
@openapi.response(200, "non dovresti essere qua...")
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.secured("token")
@auth_check
async def read_root(req: Request):
    await request_log(req, True, "non dovresti essere qua...", "")
    return text("non dovresti essere qua...")
