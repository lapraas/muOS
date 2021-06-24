
import os

import dubious

key = os.getenv("DISCORD_SECRET_MUOS")
if not key:
    with open("./sources/key.txt", "r") as f:
        key = f.read()

g = dubious.Gateway(dubious.GATEWAY_URI)
client = dubious.Client(key, (1 << 0) | (1 << 4) | (1 << 5) | (1 << 9) | (1 << 10) | (1 << 12) | (1 << 13), g)
client.start()