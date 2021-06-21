
import asyncio
import datetime as dt
import json
from typing import Optional

from websockets import client

from dubious.raw import Payload

GATEWAY_URI = "wss://gateway.discord.gg/?v=9&encoding=json"

def printWithTime(text: str):
    print(f"[{str(dt.datetime.now().time())[:-7]}] {text}")

class Gateway:
    def __init__(self, uri: str):
        self.uri = uri

        self.sendQ: asyncio.Queue[Payload] = asyncio.Queue()
        self.recvQ: asyncio.Queue[Payload] = asyncio.Queue()
        self.started = asyncio.Event()
        self.ws: client.WebSocketClientProtocol = None
        self.closedTask: Optional[asyncio.Task] = None
        self.recvTask: Optional[asyncio.Task] = None
        self.sendTask: Optional[asyncio.Task] = None
    
    def start(self, loop: asyncio.AbstractEventLoop):
        self.closedTask = loop.create_task(self.loopClosed())
        self.recvTask = loop.create_task(self.loopRecv())
        self.sendTask = loop.create_task(self.loopSend())
        loop.create_task(self.connect())
    
    async def connect(self):
        self.ws = await client.connect(self.uri)
        self.started.set()
    
    async def loopClosed(self):
        await self.started.wait()
        await self.ws.wait_closed()
        printWithTime("websocket closed\n" + f"  code: {self.ws.close_code}" + "\n" + f"  reason: {self.ws.close_reason}")
    
    async def loopRecv(self):
        await self.started.wait()
        while self.started.is_set():
            data = await self.ws.recv()
            payload: Payload = json.loads(data)
            printWithTime(f"R: {payload}")
            await self.recvQ.put(payload)
            print("put into recvQ")

    async def loopSend(self):
        await self.started.wait()
        while self.started.is_set():
            payload = await self.sendQ.get()
            data = json.dumps(payload)
            printWithTime(f"S: {payload}")
            await self.ws.send(data)
    
    async def recv(self):
        print("[Gateway] recv called")
        return await self.recvQ.get()
    
    async def send(self, payload: Payload):
        await self.sendQ.put(payload)
    
    async def stop(self, code=1000):
        self.started.clear()
        await self.recvTask
        await self.sendTask
        await self.ws.close(code)
        await self.closedTask

    async def restart(self):
        await self.stop()
        await asyncio.sleep(2)
        self.start()
        await self.connect()