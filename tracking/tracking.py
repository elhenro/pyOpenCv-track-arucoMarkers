#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
import websockets
import logging
import json
import atexit
import time
import concurrent
import positioning

logging.basicConfig(level="INFO")


sockets = set()
loop = asyncio.get_event_loop()

async def on_connect(socket, path):
    logging.info("socket connected")
    sockets.add(socket)
    try:
        while True:
            message = await socket.recv()
            logging.warning("ignore incoming message: {}", message)
    except:
        sockets.remove(socket)
        logging.info("socket disconnected (maybe in response to closing handshake)")

async def on_track(position):
    logging.info("received position")

    logging.debug(position)

    id, x, y, bearing = position
    message = {
        "id": int(id),
        "x":x,
        "y":y,
        "bearing":bearing
    }
    #message = json.dumps(message)

    for socket in sockets:
        await socket.send(json.dumps(message))

if __name__ == "__main__":
    logging.info("starting capture loop...")
    start_positioning = positioning.track(on_track)
    logging.info("starting websocket...")
    start_server = websockets.serve(on_connect, port=5678)

    logging.info("add capturer to event loop...")
    loop.run_until_complete(start_positioning)

    logging.info("add server to event loop...")
    loop.run_until_complete(start_server)
#    loop.run_until_complete(start_positioning)

    logging.info("all started")
    loop.run_forever()
