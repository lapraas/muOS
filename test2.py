
import asyncio
import os

import dubious

key = os.getenv("DISCORD_SECRET_MUOS")
if not key:
    with open("./sources/key.txt", "r") as f:
        key = f.read()

g = dubious.Gateway(dubious.GATEWAY_URI)
client = dubious.Client(key, 7, g)
client.start()