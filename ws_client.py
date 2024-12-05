import asyncio
import websockets

server_url = "ws://localhost:8001"


async def main():
    async with websockets.connect(server_url) as ws:
        while True:
            # msg = input("Enter messages: ")
            msg = ""
            if msg == "quit":
                await ws.close()
                break
            if len(msg) > 0:
                await ws.send(msg)
            response = await ws.recv()
            print(response)


if __name__ == "__main__":
    asyncio.run(main())
