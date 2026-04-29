import asyncio
from betterproto2 import Message
from common import db as database
from common import srtools
from common.util import AsyncFs, SyncFs, Log
from proto.cmd import CmdRegistry
from typing import Optional
from .packet import Packet


class Connection:
    __slots__ = (
        "reader",
        "writer",
        "db",
        "freesr_data",
        "freesr_last_modified",
        "db_last_modified",
    )

    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        db: database.DB,
        freesr_data: srtools.FreesrData,
    ):
        self.reader = reader
        self.writer = writer
        self.db = db
        self.freesr_data = freesr_data
        self.freesr_last_modified = SyncFs.get_last_modified_time(srtools.FILE_NAME)
        self.db_last_modified = SyncFs.get_last_modified_time(database.FILE_NAME)

    async def read_packet(self) -> Packet:
        return await Packet.read_from(self.reader)

    def decode_packet(self, pkt: Packet, msg: Message) -> Message:
        return msg.parse(pkt.body)

    def _encode_packet(
        self, msg: Message, override_name: Optional[str] = None
    ) -> bytes:
        msg_name = override_name or msg.__class__.__name__
        cmd = CmdRegistry.get_id(msg_name)
        pkt = Packet(cmd=cmd, body=bytes(msg))
        return bytes(pkt)

    async def _send(self, buf: bytes) -> None:
        self.writer.write(buf)
        await self.writer.drain()

    async def send_packet(
        self, msg: Message, override_name: Optional[str] = None
    ) -> None:
        buf = self._encode_packet(msg, override_name)
        await self._send(buf)

    async def send_dummy(self, cmd: int) -> None:
        buf = bytes(Packet(cmd=cmd))
        await self._send(buf)

    async def close(self) -> None:
        self.writer.close()
        await self.writer.wait_closed()

    async def save_db(self) -> None:
        try:
            await AsyncFs.write_to_file(
                database.FILE_NAME, self.db.model_dump_json(indent=2)
            )
        except Exception as e:
            Log.error(f"failed saving db: {e}")

    async def refresh_freesr(self) -> None:
        try:
            current_mtime = SyncFs.get_last_modified_time(srtools.FILE_NAME)
            if current_mtime != self.freesr_last_modified:
                Log.debug("freesr data changed")
                self.freesr_data, _ = await AsyncFs.json_parse_or_write(
                    srtools.FILE_NAME,
                    srtools.FreesrData,
                    srtools.FreesrData.default(),
                    overwrite_invalid=False,
                )
                self.freesr_last_modified = current_mtime
                Log.info("freesr data has been refreshed")
        except Exception as e:
            Log.error(f"failed refreshing freesr: {e}")

    async def refresh_db(self) -> None:
        try:
            current_mtime = SyncFs.get_last_modified_time(database.FILE_NAME)
            if current_mtime != self.db_last_modified:
                Log.debug("db changed")
                self.db, _ = await AsyncFs.json_parse_or_write(
                    database.FILE_NAME,
                    database.DB,
                    database.DB.default(),
                    overwrite_invalid=False,
                )
                self.db_last_modified = current_mtime
                Log.info("db has been refreshed")
        except Exception as e:
            Log.error(f"failed refreshing db: {e}")
