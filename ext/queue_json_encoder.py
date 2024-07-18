import json as jsonlib
from datetime import datetime
from pyrogram.raw.types import InputPeerUser

class CustomJSONEncoder(jsonlib.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, InputPeerUser):
            return {"user_id": obj.user_id, "access_hash": obj.access_hash}
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
