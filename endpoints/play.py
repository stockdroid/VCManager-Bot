import os
import time

#from pytgcalls.types import InputStream
#from pytgcalls.types.input_stream import InputAudioStream
from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from ext.auth_check import auth_check
from shared import call_py

playbp = Blueprint("playbp")


@playbp.post("/play/<file_name:str>")
@auth_check
@openapi.response(200, '{"playing": true}')
@openapi.response(204, '{"error": "FileNotFound"}')
async def play_audio(req: Request, file_name: str):
    if os.path.isfile(f"./audio/{file_name}.audio") is False:
        return json({"error": "FileNotFound"}, status=204)
    else:
        call_py.input_filename = f"./audio/{file_name}.audio"
        call_py.restart_playout()
        shared.time_started = time.time()
        call_py.play_on_repeat = False
        return json({"playing": True})

@playbp.post("/play/duration/<file_name:str>")
@auth_check
@openapi.response(200, '{"duration": <duration>}')
@openapi.response(204, '{"error": "FileNotFound"}')
async def audio_duration(req: Request, file_name: str):
    if os.path.isfile(f"./audio/{file_name}.audio") is False:
        return json({"error": "FileNotFound"}, status=204)
    else:
        size = os.path.getsize(f"./audio/{file_name}.audio")
        BIT_DEPTH = 16
        NUM_CHANNELS = 2
        SAMPLE_RATE = 48000
        duration = size / (NUM_CHANNELS*SAMPLE_RATE*(BIT_DEPTH/8))
        return json({"duration": duration})



@playbp.get("/play/status")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"elapsed": <sec>}')
async def play_status(req: Request):
    if shared.time_at_pause != 0:
        time_elapsed = shared.time_at_pause
    else:
        time_elapsed = time.time() - shared.time_started
    return json({"elapsed": time_elapsed if (time_elapsed < 100000) else None})


@playbp.patch("/play/pause")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"playing": false}')
async def pause_audio(req: Request):
    call_py.pause_playout()
    shared.time_at_pause = time.time() - shared.time_started
    return json({"playing": False})


@playbp.patch("/play/resume")
@auth_check
@openapi.response(401, '{"error": "UNAUTHORIZED"}')
@openapi.response(200, '{"playing": true}')
async def resume_audio(req: Request):
    call_py.resume_playout()
    if shared.time_at_pause != 0:
        shared.time_started = time.time() - shared.time_at_pause
        shared.time_at_pause = 0
    return json({"playing": True})
