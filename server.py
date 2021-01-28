import asyncio
import websockets
from poker import logic #(id:int, ids:list(int),message:str) -> dict(id:int, message:str)

queues = dict()
top = 0
def get_all_users():
    ret = list()
    for id,queue in queues.items():
        ret.append(id)
    ret.sort()
    return ret

class Chat():
    def __init__(self, id:int, name:str):
        self.name = name
        self.id = id
        self.left = False

async def send(ws: websockets.WebSocketServerProtocol, client:Chat):
    global queues
    while not client.left:
        msg = await queues[client.id].get()
        await ws.send(msg)

async def receive(ws: websockets.WebSocketServerProtocol, client:Chat):
    global queues
    async for msg in ws:
        ret = logic(client.id, get_all_users(), msg)
        for id,reply in ret.items():
            await queues[id].put(reply)
    client.left = True
    del queues[client.id]
    for id,queue in queues.items():
        await queue.put("系统提示: "+ f"{client.name}({client.id})" + " 的连接已断开")

async def handler(ws: websockets.WebSocketServerProtocol, path: str):
    global queues, top
    top += 1
    client = Chat(top, path[1:])
    queues[client.id] = asyncio.Queue(maxsize=10)
    for id,queue in queues.items():
        await queue.put("系统提示: "+ f"{client.name}({client.id})" + " 进入了房间")
    await asyncio.gather(receive(ws,client), send(ws,client))

async def server_starter():
    await websockets.serve(handler, '0.0.0.0', 8910)

asyncio.get_event_loop().run_until_complete(server_starter())
asyncio.get_event_loop().run_forever()