import asyncio
import websockets
from logic import logic, logic_client_connect, logic_client_disconnect

queues = dict()
names = dict()
top = 0

class Chat():
    def __init__(self, id:int, name:str):
        self.name = name
        self.id = id
        self.left = False

async def send(ws: websockets.WebSocketServerProtocol, client:Chat):
    global queues
    while not client.left:
        msg = await queues[client.id].get()
        if msg != "ACK_EXIT":
            await ws.send(msg)

async def receive(ws: websockets.WebSocketServerProtocol, client:Chat):
    global queues
    async for msg in ws:
        if msg == "EXIT":
            await ws.send("ACK_EXIT")
            break
        ret = logic(client.id, names.copy(), msg)
        for id,reply in ret.items():
            await queues[id].put(reply)
    client.left = True
    clientname = client.name
    del queues[client.id]
    del names[client.id]
    ret = logic_client_disconnect(client.id, clientname, names.copy())
    for id,reply in ret.items():
        await queues[id].put(reply)

async def handler(ws: websockets.WebSocketServerProtocol, path: str):
    global queues, top
    top += 1
    client = Chat(top, path[1:])
    queues[client.id] = asyncio.Queue(maxsize=10)
    names[client.id] = path[1:]
    ret = logic_client_connect(client.id, names.copy())
    for id,reply in ret.items():
        await queues[id].put(reply)
    await asyncio.gather(receive(ws,client), send(ws,client))

async def server_starter():
    await websockets.serve(handler, '0.0.0.0', 8910)

asyncio.get_event_loop().run_until_complete(server_starter())
asyncio.get_event_loop().run_forever()