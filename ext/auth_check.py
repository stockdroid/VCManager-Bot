import os
import time
from functools import wraps
from typing import Optional

import jwt
from dotenv import load_dotenv
from sanic import Request
from sanic.response import json

import shared
from ext.log_helper import auth_error

load_dotenv()


async def check_token(request: Request) -> Optional[str]:
    if shared.ENABLE_CF_AUTH:
        try:
            auth: str = request.headers.getone("Authorization")
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
                break
            except:
                pass
        return None
    else:
        return None


def auth_check(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request: Request, *args, **kwargs):
            is_authenticated = await check_token(request)

            if is_authenticated is not None or not shared.ENABLE_CF_AUTH:
                request.ctx.email = is_authenticated
                response = await f(request, *args, **kwargs)
                return response
            else:
                return json({"error": "UNAUTHORIZED"}, 401)

        return decorated_function

    return decorator(wrapped)
