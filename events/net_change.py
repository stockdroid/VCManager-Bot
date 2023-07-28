import json

from shared import ws_list


async def net_change(_, is_connected):
    for ws in ws_list:
        await ws.send(
            json.dumps({
                "action": f"NET_CHANGE",
                "data": {
                    "connected": is_connected
                }
            })
        )
