import asyncio
import traceback
from common import db
from common import srtools
from common.util import AsyncFs, Log
from proto.cmd import CmdRegistry
from .handler import HANDLER_MAP, DUMMY_MAP
from .connection import Connection


async def handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    addr = writer.get_extra_info("peername")
    c: Connection = None

    try:
        my_data, did_overwrite = await AsyncFs.json_parse_or_write(
            db.FILE_NAME, db.DB, db.DB.default(), overwrite_invalid=True
        )
        if did_overwrite:
            Log.error(f"{db.FILE_NAME} was invalid or missing")
            Log.warn("It has been overwritten.")

        freesr_data, did_overwrite = await AsyncFs.json_parse_or_write(
            srtools.FILE_NAME,
            srtools.FreesrData,
            srtools.FreesrData.default(),
            overwrite_invalid=True,
        )
        if did_overwrite:
            Log.error(f"{srtools.FILE_NAME} was invalid or missing")
            Log.warn("It has been overwritten.")

        c = Connection(reader, writer, my_data, freesr_data)
        while True:
            try:
                pkt = await c.read_packet()
                cmd = pkt.cmd
            except EOFError:
                break

            try:
                cmd_name = CmdRegistry.get_name(cmd)
                Log.debug(f"got {cmd_name} ({cmd}) from {addr}")
            except ValueError:
                Log.warn(f"got UnregisteredCmd ({cmd}) from {addr}")
                continue

            if handler := HANDLER_MAP.get(cmd):
                try:
                    await handler(c, pkt)
                except Exception as e:
                    Log.error(f"handler error {cmd_name} ({cmd}): {e}")
                    Log.error(f"==== TRACEBACK =====\n{traceback.format_exc()}")
                    Log.error("==== TRACEBACK =====")
            elif rsp_cmd := DUMMY_MAP.get(cmd):
                await c.send_dummy(rsp_cmd)
            else:
                Log.warn(f"unhandled cmd: {cmd_name} ({cmd})")

    except Exception as e:
        Log.error(f"client error {addr}: {e}")
        Log.error(f"==== TRACEBACK =====\n{traceback.format_exc()}")
        Log.error("==== TRACEBACK =====")
    finally:
        if c:
            await c.close()
        Log.info(f"client {addr} disconnected.")
