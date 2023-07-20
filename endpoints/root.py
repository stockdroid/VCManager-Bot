from sanic import Blueprint, Request, text

rootBp = Blueprint("root")


@rootBp.get("/")
async def read_root(req: Request):
    return text("non dovresti essere qua...")
