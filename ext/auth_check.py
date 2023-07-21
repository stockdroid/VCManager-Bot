import os
from functools import wraps

import jwt
from dotenv import load_dotenv
from sanic import Request
from sanic.response import json

import shared

load_dotenv()


def check_token(request: Request):
    if not request.token:
        return False

    valid_token = False
    for key in shared.public_keys:
        try:
            # decode returns the claims that has the email when needed
            jwt.decode(request.token, key=key, audience=os.environ.get('CF_AUD'), algorithms=['RS256'])
            valid_token = True
            break
        except:
            pass
    return valid_token


def auth_check(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authenticated = check_token(request)

            if is_authenticated or not shared.ENABLE_CF_AUTH:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return json({"error": "UNAUTHORIZED"}, 401)

        return decorated_function

    return decorator(wrapped)
