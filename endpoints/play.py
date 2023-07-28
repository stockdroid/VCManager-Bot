import os
import time

from pytgcalls.exceptions import CallBeforeStartError
from sanic import Blueprint, Request, json
from sanic_ext.extensions.openapi import openapi

import shared
from ext.auth_check import auth_check
from ext.log_helper import request_log
from shared import call_py
import json as jsonlib

playbp = Blueprint("playbp")


@playbp.post("/play/<file_name:str>")
@openapi.secured("token")
@openapi.response(200, {"application/json": {"playing": True}})
@openapi.response(400, {"application/json": {"error": "FileNotFound"}})
@openapi.response(406, {"application/json": {"error": "NotInVC"}})
@auth_check
async def play_audio(req: Request, file_name: str):
    if os.path.isfile(f"./audio/{file_name}.audio") is False:
        await request_log(req, False, "", jsonlib.dumps({"error": "FileNotFound"}))
        return json({"error": "FileNotFound"}, status=400)
    else:
        try:
            call_py.input_filename = f"./audio/{file_name}.audio"
            call_py.restart_playout()
            shared.time_started = time.time()
            call_py.play_on_repeat = False
            await request_log(req, True, jsonlib.dumps({"playing": True}), "")
            for ws in shared.ws_list:
                await ws.send(
                    jsonlib.dumps({
                        "action": f"AUDIO_STATE_UPDATE",
                        "data": {
                            "state": "PLAY",
                            "seconds": 0
                        }
                    })
                )
            return json({"playing": True})
        except CallBeforeStartError:
            await request_log(req, True, "", jsonlib.dumps({"error": "NotInVC"}))
            return json({"error": "NotInVC"}, 406)


@playbp.get("/play/list")
@openapi.secured("token")
@openapi.response(200, {"application/json": {"filenames": []}})
@auth_check
async def list_files(req: Request):
    files_list = os.listdir("./audio")
    await request_log(req, True, jsonlib.dumps({"filenames": files_list}), "")
    return json({"filenames": files_list})


@playbp.post("/play/duration/<file_name:str>")
@openapi.secured("token")
@openapi.response(200, {"application/json": {"duration": 4}})
@openapi.response(400, {"application/json": {"error": "FileNotFound"}})
@auth_check
async def audio_duration(req: Request, file_name: str):
    if os.path.isfile(f"./audio/{file_name}.audio") is False:
        await request_log(req, False, "", jsonlib.dumps({"error": "FileNotFound"}))
        return json({"error": "FileNotFound"}, status=400)
    else:
        size = os.path.getsize(f"./audio/{file_name}.audio")
        BIT_DEPTH = 16
        NUM_CHANNELS = 2
        SAMPLE_RATE = 48000
        duration = size / (NUM_CHANNELS * SAMPLE_RATE * (BIT_DEPTH / 8))
        await request_log(req, True, jsonlib.dumps({"duration": duration}), "")
        return json({"duration": duration})


@playbp.get("/play/status")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"elapsed": 6}})
@auth_check
async def play_status(req: Request):
    if shared.time_at_pause != 0:
        time_elapsed = shared.time_at_pause
    else:
        time_elapsed = time.time() - shared.time_started
    await request_log(req, True, jsonlib.dumps({"elapsed": time_elapsed if (time_elapsed < 100000) else None}), "")
    return json({"elapsed": time_elapsed if (time_elapsed < 100000) else None})


@playbp.patch("/play/pause")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"playing": False}})
@auth_check
async def pause_audio(req: Request):
    call_py.pause_playout()
    shared.time_at_pause = time.time() - shared.time_started
    await request_log(req, True, jsonlib.dumps({"playing": False}), "")
    for ws in shared.ws_list:
        await ws.send(
            jsonlib.dumps({
                "action": f"AUDIO_STATE_UPDATE",
                "data": {
                    "state": "PAUSE",
                    "seconds": shared.time_at_pause
                }
            })
        )
    return json({"playing": False})


@playbp.patch("/play/resume")
@openapi.secured("token")
@openapi.response(401, {"application/json": {"error": "UNAUTHORIZED"}})
@openapi.response(200, {"application/json": {"playing": True}})
@auth_check
async def resume_audio(req: Request):
    call_py.resume_playout()
    if shared.time_at_pause != 0:
        shared.time_started = time.time() - shared.time_at_pause
        shared.time_at_pause = 0
    await request_log(req, True, jsonlib.dumps({"playing": True}), "")
    for ws in shared.ws_list:
        await ws.send(
            jsonlib.dumps({
                "action": f"AUDIO_STATE_UPDATE",
                "data": {
                    "state": "RESUME",
                    "seconds": shared.time_started
                }
            })
        )
    return json({"playing": True})
