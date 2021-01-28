import asyncio
import websockets
import sys

async def send(ws):
    '''
    Read user input in a asynchoronous function: event loop
    Code pieces and idea from SAST 
    '''
    loop = asyncio.get_event_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        #print('\r',end="")
        msg = line[0:-1]
        await ws.send(msg)


async def receive(ws):
    async for msg in ws:
        print(msg)

async def main():
    name = input("Input your name(A-z 0-9):")
    IP = input("服务器IP地址(点分十进制):")
    uri = f"ws://{IP}:8910/{name}"
    async with websockets.connect(uri) as websocket:
        await asyncio.gather(send(websocket),receive(websocket))

asyncio.run(main())