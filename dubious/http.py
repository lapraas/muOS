
import asyncio
import json

import requests

_VERSION = "v9"
BASE_URL = f"https://discord.com/api/{_VERSION}"

def req(endpoint: str):
    return json.loads(requests.get(BASE_URL + endpoint).text)

class ENDPOINTS:
    GUILD = "/guilds"