import os
import time
from functools import wraps
from typing import Optional

import jwt
import requests
from dotenv import load_dotenv
from sanic import Request
from sanic.response import json

import shared
from ext.log_helper import auth_error

load_dotenv()


async def check_token(request: Request) -> Optional[str]:
    if shared.ENABLE_CF_AUTH:
        try:
            auth: str = request.args.get("authorization") or request.headers.getone("Authorization")
            auth = auth.replace("Bearer ", "").replace("Token ", "")
        except KeyError:
            await auth_error("NA", request.url, request.method, "NO_AUTH_TOKEN")
            return None

        for key in shared.public_keys:
            try:
                # decode returns the claims that has the email when needed
                decoded = jwt.decode(auth, key=key, audience=os.environ.get('CF_AUD'), algorithms=['RS256'])
                email: str = decoded["email"]
                if decoded["exp"] < int(time.time()):
                    await auth_error(email, request.url, request.method, "EXPIRED_TOKEN")
                    return None
                else:
                    if not email.endswith(os.environ.get("EMAIL_CHECK")):
                        await auth_error(email, request.url, request.method, "EMAIL_INVALID")
                        return None
                    else:
                        return email
            except:
                pass
        return None
    else:
        return None


async def get_ext_info(req: Request):
    auth: str = req.args.get("authorization") or req.headers.getone("Authorization")
    auth = auth.replace("Bearer ", "").replace("Token ", "")
    for key in shared.public_keys:
        try:
            # decode returns the claims that has the email when needed
            decoded = jwt.decode(auth, key=key, audience=os.environ.get('CF_AUD'), algorithms=['RS256'])
            if decoded["identity_nonce"] not in shared.cached_ext.keys():
                identity = requests.get(
                    f"https://{os.environ.get('CF_URL')}/cdn-cgi/access/get-identity",
                    headers={"Cookie": f"CF_Authorization={auth}"}
                ).json()
                req.ctx.name = identity["name"]
                req.ctx.groups = identity["groups"]
                shared.cached_ext[decoded["identity_nonce"]] = identity
            else:
                identity = shared.cached_ext[decoded["identity_nonce"]]
                req.ctx.name = identity["name"]
                req.ctx.groups = identity["groups"]
        except:
            pass


def auth_check(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request: Request, *args, **kwargs):
            is_authenticated = await check_token(request)

            if is_authenticated is not None or not shared.ENABLE_CF_AUTH:
                request.ctx.email = is_authenticated
                await get_ext_info(request) if shared.ENABLE_CF_AUTH else None
                response = await f(request, *args, **kwargs)
                return response
            else:
                return json({"error": "UNAUTHORIZED"}, 401)

        return decorated_function

    return decorator(wrapped)
