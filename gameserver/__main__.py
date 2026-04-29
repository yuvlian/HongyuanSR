import asyncio
from common import GAMESERVER_ADDR
from common.res import load_res
from common.util import Log
from .client import handle_client


async def start_server() -> None:
    await load_res()
    Log.info("res loaded.")
    host, port = GAMESERVER_ADDR
    server = await asyncio.start_server(handle_client, host, port)
    Log.info(f"gameserver listening on {host}:{port}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        pass
