from sanic import Blueprint, Request, json

rootBp = Blueprint("root")


@rootBp.get("/")
async def read_root(req: Request):
    return json({"Hello": "World"})
