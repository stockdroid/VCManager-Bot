from sanic import Blueprint, Request, text
from sanic_ext.extensions.openapi import openapi

from ext.auth_check import auth_check
from ext.log_helper import request_log
from models.general import ResponseError

rootBp = Blueprint("root")


@rootBp.get("/")
@openapi.response(200, "non dovresti essere qua...")
@openapi.response(401, {"application/json": ResponseError("UNAUTHORIZED")})
@openapi.summary("Api root")
@openapi.description("The root of the api, it can be used as an auth check")
@openapi.secured("token")
@auth_check
async def read_root(req: Request):
    await request_log(req, True, "non dovresti essere qua...", "")
    return text("non dovresti essere qua...")
