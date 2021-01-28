import asyncio
import websockets
import sys

async def send(ws):
    '''
    Read user input in a asynchoronous function: event loop
    Code pieces and idea from THU-CST SAST
    '''
    loop = asyncio.get_event_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        msg = line[0:-1]
        await ws.send(msg)
        if msg == "EXIT":
            break


async def receive(ws):
    async for msg in ws:
        if msg == "ACK_EXIT":
            break
        print(msg)

async def main():
    name = "THIRD"#要使用的用户名
    IP = "127.0.0.1"#服务器IP地址,需要改成真实地址
    port = "8910"#端口
    uri = f"ws://{IP}:{port}/{name}"
    async with websockets.connect(uri) as websocket:
        await asyncio.gather(send(websocket),receive(websocket))

asyncio.run(main())