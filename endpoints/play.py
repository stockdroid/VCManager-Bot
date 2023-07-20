import time

from pytgcalls.types import InputStream
from pytgcalls.types.input_stream import InputAudioStream
from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from shared import call_py

playbp = Blueprint("playbp")


@playbp.post("/play/<file_name:str>")
@openapi.response(200, '{"playing": true}')
@openapi.response(204, '{"error": "FileNotFound"}')
async def play_audio(req: Request, file_name: str):
    try:
        await call_py.change_stream(shared.GROUP_ID, InputStream(InputAudioStream(f"./audio/{file_name}.audio")))
        time.sleep(0.5)
        await call_py.pause_stream(shared.GROUP_ID)
        time.sleep(0.5)
        await call_py.resume_stream(shared.GROUP_ID)
        return json({"playing": True})
    except FileNotFoundError:
        return json({"error": "FileNotFound"}, status=204)


@playbp.get("/play/status")
@openapi.response(200, '{"elapsed": <sec>}')
async def play_status(req: Request):
    return json({"elapsed": await call_py.played_time(shared.GROUP_ID)})


@playbp.patch("/play/pause")
@openapi.response(200, '{"playing": false}')
async def pause_audio(req: Request):
    await call_py.pause_stream(shared.GROUP_ID)
    return json({"playing": False})


@playbp.patch("/play/resume")
@openapi.response(200, '{"playing": true}')
async def resume_audio(req: Request):
    await call_py.resume_stream(shared.GROUP_ID)
    return json({"playing": True})
