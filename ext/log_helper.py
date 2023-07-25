import asyncio
import os
import time

from dotenv import load_dotenv
from sanic.request import Request

from shared import tg_app, DEV_MODE

load_dotenv()


async def _send_log_msg(mess: str):
    await tg_app.get_chat(int(os.environ.get(f"LOG_CHANNEL{'_DEV' if DEV_MODE else ''}")))
    await tg_app.send_message(int(os.environ.get(f"LOG_CHANNEL{'_DEV' if DEV_MODE else ''}")), mess)


def _gen_log_txt(
        email: str, endpoint: str, method: str, success: bool, errored: bool, response: str, error: str
):
    email_domain: str = os.environ.get('EMAIL_CHECK')
    email_username = email.replace(email_domain, '')
    api: str = endpoint.replace("://", "").split("/")[1]

    to_return = f"#email{email_username}, #endpoint{api}, #method{method}, " \
                f"{'#success' if success else '#errored' if errored else ''}\n\n"

    to_return += f"Email: {email}\n"
    to_return += f"URL: {endpoint}\n"
    to_return += f"Method: {method}\n"
    to_return += f"Succeded: {success}\n"
    to_return += f"Response: {response if (len(response) <= 1000) else 'too long to send'}\n" if (response != "") else f"Error: {error}\n"
    to_return += f"Timestamp: {int(time.time())}\n"

    return to_return


async def part_change_log(joined: bool, id: int, username: str, name: str):
    to_return = f"#{'join' if joined else 'quit'}, #user{id}\n\n"

    to_return += f"Joined: {'yes' if joined else 'no'}\n"
    to_return += f"User ID: {id}\n"
    to_return += f"Username: {username}\n"
    to_return += f"Name: {name}\n"
    to_return += f"Timestamp: {int(time.time())}\n"

    await _send_log_msg(to_return)


def vc_action_log(muted: bool, id: int, username: str, name: str):
    to_return = f"#{'muted' if muted else 'unmuted'}, #user{id}\n\n"

    to_return += f"Muted: {'yes' if muted else 'no'}\n"
    to_return += f"User ID: {id}\n"
    to_return += f"Username: {username}\n"
    to_return += f"Name: {name}\n"
    to_return += f"Timestamp: {int(time.time())}\n"

    asyncio.run(_send_log_msg(to_return))


async def play_ended_log():
    to_return = f"#playended\n\n"

    to_return += f"Play ended: yes\n"
    to_return += f"Timestamp: {int(time.time())}\n"

    await _send_log_msg(to_return)


async def auth_error(email: str, endpoint: str, method: str, error: str):
    await _send_log_msg(_gen_log_txt(
        email, endpoint, method, False, True, "", error
    ))


async def request_log(req: Request, success: bool, response: str, error: str):
    await _send_log_msg(_gen_log_txt(
        req.ctx.email, req.url, req.method, success, not success, response, error
    ))
