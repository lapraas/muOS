
import asyncio
import json
import os

import nest_asyncio
import requests

import dubious

nest_asyncio.apply()

_VERSION = "v9"
BASE_URL = f"https://discord.com/api/{_VERSION}/"

def httpReq(endpoint: str):
    return json.loads(requests.get(BASE_URL + endpoint).text)

async def main():
    key = os.getenv("DISCORD_SECRET_MUOS")
    if not key:
        with open("./sources/key.txt", "r") as f:
            key = f.read()
    client = dubious.Client(
        token=key,
        intents=7,#(1 << 0) | (1 << 4) | (1 << 5) | (1 << 9) | (1 << 10) | (1 << 12) | (1 << 13),
        req=dubious.Requester(httpReq("gateway")["url"] + "?v=9&encoding=json")
    )
    await client.start()

asyncio.get_event_loop().run_until_complete(main())
