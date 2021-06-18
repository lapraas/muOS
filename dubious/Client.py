
from __future__ import annotations

import asyncio
import sys
from typing import Callable, Coroutine, Optional, Union

import dubious.raw as raw
from dubious.Gateway import Gateway
from dubious.types import Application, User

class HandlesEvents:
    handlers: dict[int, Callable[[raw.Payload], Coroutine]]

    def __init__(self):
        self.handlers = {}
        for attrName in dir(self):
            attr = self.__getattribute__(attrName)
            if not callable(attr): continue
            if attrName in raw.EVENT.__dict__:
                self.handlers[raw.EVENT.__dict__[attrName]] = attr
    
    def getHandler(self, t: str):
        if not t in raw.EVENT.__dict__.values():
            raise Exception(f"{t} is not a valid event.")
        if not t in self.handlers:
            raise NotImplementedError()
        return self.handlers[t]

class Client(HandlesEvents):
    def __init__(self, token: str, intents: int, gateway: Gateway):
        super().__init__()
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
        # The last sequence number gotten with a recieved payload.
        self.sequence: Optional[int] = None

        # Whether or not the Client has recieved the Ready event.
        self.ready = asyncio.Event()
        # The version of the gateway api being used.
        self.gatewayVersion: Optional[int] = None
        self.user: Optional[User] = None
        self.sessionID: Optional[str] = None
        self.application: Optional[Application] = None
        self.rawGuilds: Optional[list[raw.UnavailableGuild]] = None

        self.handlers = {**self.handlers,
            1: self.onBeat,
            9: self.onConnectionLost,
            10: self.onHello,
            11: self.onBeatAck
        }

        self.beatAcked.set()

    def start(self):
        """ Starts the listen loop and the beat loop for the Client.
            Starts the Gateway's loops.
            Runs the asyncio loop forever. """
        loop = asyncio.get_event_loop()
        loop.create_task(self.loopRecv())
        loop.create_task(self.loopBeat())
        self.gateway.start(loop)
        asyncio.run(self.gateway.connect())
    
    async def recv(self):
        payload = await self.gateway.recv()
        op = payload["op"]
        t = payload["t"]
        self.sequence = payload["s"] if payload["s"] != None else self.sequence
        d = payload["d"]
        if t:
            handler = self.getHandler(t)
        else:
            handler = self.handlers.get(op)
        if handler:
            print(f"[Client] calling handler for {op}:{t}")
            await handler(d)
            print("[Client] done with handler")
        else:
            raise NotImplementedError()
    
    async def loopRecv(self):
        while True:
            await self.recv()
            
        
    async def beat(self):
        await self.beating.wait()
        await asyncio.sleep(self.beatTime / 1000)
        if self.beatAcked.is_set():
            self.beatAcked.clear()
            await self.sendBeat()
        else:
            await self.reconnect()
        
    async def loopBeat(self):
        while True:
            await self.beat()
    
    async def onBeat(self, _):
        """ Callback for opcode 1. """
        await self.sendBeat()
    
    async def onConnectionLost(self, _):
        """ Callback for opcode 9. """
        await self.reconnect()
    
    async def onHello(self, payload: raw.Hello):
        """ Callback for opcode 10.
            Sets the heartbeat interval and unblocks the heartbeat loop.
            Sends a heartbeat payload, then waits to send an identify payload."""
        self.beatTime = payload["heartbeat_interval"]
        self.beating.set()
        await self.sendBeat()
        await asyncio.sleep(3)
        await self.sendIdentify()

    async def onBeatAck(self, _):
        """ Callback for opcode 11.
            Sets a flag that the last heartbeat was acknowledged. """
        print("beat acknowledged")
        self.beatAcked.set()
    
    async def onReady(self, payload: raw.Ready):
        """ Callback for event READY.
            Stores the client's User object, the session ID, the client's Application object, and the incomplete Guild objects.
            Sets the ready flag. """
        self.gatewayVersion = payload["v"]
        self.user = User(payload["user"])
        self.sessionID = payload["session_id"]
        self.application = Application(payload["application"])
        self.rawGuilds = payload["guilds"]
        self.ready.set()
    
    async def onResumed(self, _):
        """ Callback for event RESUMED.
            Sets the ready flag. """
        self.ready.set()
    
    async def onReconnect(self, _):
        """ Callback for event RECONNECT.
            Calls the reconnect routine. """
        await self.reconnect()
    
    async def sendBeat(self):
        """ Sends a heartbeat payload. """
        await self.gateway.send({
            "op": 1,
            "d": self.sequence
        })
    
    async def sendIdentify(self):
        """ Sends an identify payload. """
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
    
    async def reconnect(self):
        """ Clears the ready flag.
            Restarts the gateway's websocket connection.
            Sends a reconnect payload. """

        self.ready.clear()
        await self.gateway.restart()
        
        await self.gateway.send({
            "op": 6,
            "d": {
                "token": self.token,
                "session_id": self.sessionID,
                "seq": self.sequence
            }
        })
