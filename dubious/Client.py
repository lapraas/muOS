
from __future__ import annotations

import asyncio
import sys
from typing import Optional

from dubious.Gateway import Gateway
import dubious.raw as raw
from dubious.types import User, Application


class Client:
    def __init__(self, token: str, intents: int, gateway: Gateway):
        # The client's secret.
        self.token = token
        # The intents for the client.
        self.intents = intents
        # The connection to the websocket through which to recieve and request information.
        self.gateway = gateway

        # The time between heartbeats in milliseconds.
        self.beatTime: Optional[int] = None
        # Starts as true for the first heartbeat.
        self.beatAcked = asyncio.Event()
        # Whether or not the heartbeat loop is active.
        self.beating = asyncio.Event()

        # Whether or not the Client has recieved the Ready event.
        self.ready = asyncio.Event()
        # The version of the gateway api being used.
        self.gatewayVersion: Optional[int] = None
        self.user: Optional[User] = None
        self.sessionID: Optional[str] = None
        self.application: Optional[Application] = None
        self.guildIDs: Optional[list[raw.UnavailableGuild]] = None

        self.handlers = {
            10: self.onHello,
            11: self.onHelloAck,
            "READY": self.onReady,
        }

    async def start(self):
        loop = asyncio.get_running_loop()
        loop.create_task(self.loopRecv())
        loop.create_task(self.loopBeat())
        await self.gateway.start()
        loop.run_forever()
    
    async def loopRecv(self):
        while True:
            payload = await self.gateway.recv()
            op = payload["op"]
            t = payload["t"]
            d = payload["d"]
            if t:
                handler = self.handlers.get(t)
            else:
                handler = self.handlers.get(op)
            if handler:
                await handler(d)
            else:
                raise NotImplementedError()
        
    async def loopBeat(self):
        while True:
            await self.beating.wait()
            await asyncio.sleep(self.beatTime / 1000)
            if self.beatAcked.is_set():
                await self.sendBeat()
                await self.beatAcked.clear()
            else:
                await self.sendReconnect()
    
    async def onHello(self, payload: raw.Hello):
        self.beatTime = payload["heartbeat_interval"]
        await asyncio.sleep(2)
        self.beating.set()
        await asyncio.sleep(3)
        await self.sendIdentify()

    async def onHelloAck(self, _):
        self.beatAcked.set()
    
    async def onReady(self, payload: raw.Ready):
        self.gatewayVersion = payload["v"]
        self.user = User(payload["user"])
        self.guildIDs = payload["guilds"]
        self.ready.set()
    
    async def sendBeat(self):
        await self.gateway.send({
            "op": 1,
            "d": None
        })
    
    async def sendReconnect(self):
        await self.gateway.send({
            "op": 6,
        })
    
    async def sendIdentify(self):
        await self.gateway.send({
            "op": 2,
            "d": {
                "token": self.token,
                "intents": self.intents,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "dubious",
                    "$device": "dubious"
                }
            }
        })
