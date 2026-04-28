import asyncio
import struct


HEAD_MAGIC = b"\x9d\x74\xc7\x14"
TAIL_MAGIC = b"\xd7\xa1\x52\xc8"


class Packet:
    __slots__ = ("cmd", "head", "body")

    def __init__(self, cmd: int = 0, head: bytes = b"", body: bytes = b""):
        self.cmd = cmd
        self.head = head
        self.body = body

    def __bytes__(self) -> bytes:
        head_len = len(self.head)
        body_len = len(self.body)
        total_len = 12 + head_len + body_len + 4

        buf = bytearray(total_len)
        view = memoryview(buf)

        view[0:4] = HEAD_MAGIC
        struct.pack_into(">HHI", view, 4, self.cmd, head_len, body_len)

        offset = 12
        if head_len > 0:
            view[offset : offset + head_len] = self.head
            offset += head_len

        if body_len > 0:
            view[offset : offset + body_len] = self.body
            offset += body_len

        view[offset : offset + 4] = TAIL_MAGIC

        return bytes(buf)

    @classmethod
    async def read_from(cls, reader: asyncio.StreamReader) -> "Packet":
        try:
            header_data = await reader.readexactly(12)
        except asyncio.IncompleteReadError:
            raise EOFError("conn closed")

        if header_data[:4] != HEAD_MAGIC:
            raise ValueError("invalid head magic")

        cmd, head_len, body_len = struct.unpack_from(">HHI", header_data, 4)

        try:
            buf = await reader.readexactly(head_len + body_len + 4)
            head = buf[:head_len]
            body = buf[head_len : head_len + body_len]
            tail = buf[-4:]
        except asyncio.IncompleteReadError:
            raise EOFError("conn closed")

        if tail != TAIL_MAGIC:
            raise ValueError("invalid tail magic")

        return cls(cmd=cmd, head=head, body=body)
