import json
import time

import pyrogram
from pyrogram.raw.base.messages import ChatFull
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.phone import GetGroupParticipants
from sanic import Request, Websocket, Blueprint

from ext.auth_check import auth_check
from shared import call_py, tg_app, GROUP_ID, ws_list

ws_bp = Blueprint("wsbp")


@ws_bp.websocket("/stream")
@auth_check
async def ws_stream(request: Request, ws: Websocket):
    data = json.dumps({
        "action": "INTRODUCTION",
        "data": {}
    })
    print("Sending: " + data)
    await ws.send(data)

    ws_list.append(ws)

    while True:
        data = await ws.recv()
        data_json = json.loads(data)

        if data_json["action"] == "GET_PART":
            chat: ChatFull = await tg_app.invoke(GetFullChannel(channel=await tg_app.resolve_peer(GROUP_ID)))
            if chat.full_chat.call is None:
                await ws.send(json.dumps(
                    {
                        "action": "PART_ERR",
                        "data": {
                            "SPECIFIC": "NoCall"
                        }
                    }
                ))
            else:
                participants_list = (await tg_app.invoke(GetGroupParticipants(
                    call=chat.full_chat.call, ids=[], sources=[], offset="", limit=-1
                ))).participants
                await ws.send(json.dumps(
                    {
                        "action": "PART_ACK",
                        "data": json.loads(str(participants_list))
                    }
                ))
        else:
            await ws.send(json.dumps(
                {
                    "action": "UNRECOGNIZED",
                    "data": {}
                }
            ))
