
from __future__ import annotations

import asyncio
import sys
from typing import Optional

import dubious.raw as raw
import dubious.payload as payload
from dubious.Gateway import Gateway
from dubious.types import Guild, User

class Client(payload.HandlesEvents):
    def __init__(self, token: str, intents: int, gateway: Gateway):
        super().__init__()
        # The client's secret.
        self.token = token
        # The intents for the client.
        self.intents = intents
        # The connection to the websocket through which to recieve and request information.
        self.gateway = gateway

        self.stopped = asyncio.Event()

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
        self.unavailableGuilds: Optional[list[payload.RawUnavailableGuild]] = None

        self.guilds: dict[int, raw.RawGuild] = {}

        self.handlers = {**self.handlers,
            1: self.onBeat,
            9: self.onConnectionLost,
            10: self.onHello,
            11: self.onBeatAck
        }

        self.beatAcked.set()

    ###
    # Asyncio stuff
    ###

    def start(self):
        """ Starts the listen loop and the beat loop for the Client.
            Starts the Gateway's loops.
            Runs the asyncio loop forever. """
        try:
            loop = asyncio.get_event_loop()
            self.gateway.start(loop)
            taskRecv = loop.create_task(self.loopRecv())
            taskBeat = loop.create_task(self.loopBeat())
            loop.run_forever()
        except KeyboardInterrupt:
            print("Interrupted, stopping tasks")
            self.stopped.set()
            for task in asyncio.all_tasks(loop):
                print(task)
            loop.run_until_complete(self.gateway.stop())
            loop.run_until_complete(taskRecv)
            loop.run_until_complete(taskBeat)
        finally:
            loop.close()
            print("Done")
    
    async def loopRecv(self):
        while not self.stopped.is_set():
            try:
                payload = await asyncio.wait_for(self.gateway.recv(), timeout=1)
            except asyncio.TimeoutError:
                continue
            op = payload["op"]
            t = payload["t"]
            self.sequence = payload["s"] if payload["s"] != None else self.sequence
            d = payload["d"]
            if t:
                handler = self.getHandler(t)
            else:
                handler = self.handlers.get(op)
            if handler:
                await handler(d)
            else:
                print(f"Not implemented: {t}")
        
    async def loopBeat(self):
        while not self.stopped.is_set():
            try:
                await asyncio.wait_for(self.beating.wait(), timeout=1)
            except asyncio.TimeoutError:
                continue
            _, toCancel = await asyncio.wait({
                asyncio.sleep(self.beatTime / 1000),
                self.stopped.wait()
            }, return_when=asyncio.FIRST_COMPLETED)
            for task in toCancel:
                task.cancel()
            if self.stopped.is_set():
                continue
            if self.beatAcked.is_set():
                self.beatAcked.clear()
                await self.sendBeat()
            else:
                await self.reconnect()
    
    ###
    # Callbacks
    ###

    async def onBeat(self, _):
        """ Callback for opcode 1. """
        await self.sendBeat()
    
    async def onConnectionLost(self, _):
        """ Callback for opcode 9. """
        await self.reconnect()
    
    async def onHello(self, payload: payload.Hello):
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
        self.beatAcked.set()
    
    async def onReady(self, payload: payload.Ready):
        """ Callback for event READY.
            Stores the client's User object, the session ID, the client's Application object, and the incomplete Guild objects.
            Sets the ready flag. """
        self.gatewayVersion = payload["v"]
        self.user = User(payload["user"])
        self.sessionID = payload["session_id"]
        self.unavailableGuilds = payload["guilds"]
        self.ready.set()
    
    async def onResumed(self, _: payload.Resumed):
        """ Callback for event RESUMED.
            Sets the ready flag. """
        self.ready.set()
    
    async def onReconnect(self, _: payload.Reconnect):
        """ Callback for event RECONNECT.
            Calls the reconnect routine. """
        await self.reconnect()
    
    async def onInvalidSession(self, reconnectable: payload.InvalidSession):
        """ Callback for event INVALID_SESSION.
            If the recieved value was true, attempt to reconnect. """
        if reconnectable:
            await self.reconnect()
        
    async def onGuildCreate(self, guild: raw.RawGuild):
        """ Callback for event GUILD_CREATE.
            Stores the guild in the client's cache. """
        guild = Guild(guild)
        print(f"got guild {guild.name}")
        
    ###
    # Payload sending
    ###

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
