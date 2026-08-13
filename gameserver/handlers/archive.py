from proto import ArchiveData, GetArchiveDataScRsp

from ..connection import Connection
from ..handler import handler
from ..packet import Packet


@handler
async def on_get_archive_data(c: Connection, pkt: Packet) -> None:
    await c.send_packet(GetArchiveDataScRsp(archive_data=ArchiveData()))
