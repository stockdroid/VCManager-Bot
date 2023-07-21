from sanic import Blueprint, Request, text

from ext.auth_check import auth_check

rootBp = Blueprint("root")


@rootBp.get("/")
@auth_check
async def read_root(req: Request):
    return text("non dovresti essere qua...")
