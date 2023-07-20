import os

from dotenv import load_dotenv
from pyrogram import Client
from pytgcalls import PyTgCalls

load_dotenv()


DEV_MODE = True
COMMANDS_ENABLED = False
GROUP_ID = -1001692353473
DEF_LIMIT = 2 if DEV_MODE else 30
limit = DEF_LIMIT
muted_queue = []

DEF_WHITELIST = [
    125703811,
    600788276,
    19789473,
    824343989,
    1123590296,
    739236767,
    794489469,
    704625262,
    815288701,
    775851562,
    689390665,
    507652269,
    345203403,
    1618001431,
    221748789,
    680552973,
    27856832,
    828056346,
    74911939,
    5570289840,
    224016528,
    610215341
]

whitelist = [
    125703811,
    600788276,
    19789473,
    824343989,
    1123590296,
    739236767,
    794489469,
    #704625262,
    815288701,
    775851562,
    689390665,
    507652269,
    345203403,
    1618001431,
    221748789,
    680552973,
    27856832,
    828056346,
    74911939,
    5570289840,
    224016528
]
unmuted_list = []

PHONE_NUMBER = os.environ.get(f"PHONE{'_DEV' if DEV_MODE else ''}")
API_ID = os.environ.get(f"API_ID")
API_HASH = os.environ.get(f"API_HASH")

tg_app = Client("vcmanager", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER)
call_py = PyTgCalls(tg_app)