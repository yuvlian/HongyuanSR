from enum import StrEnum
from types import SimpleNamespace

# this is so we can call all handlers when registering them
# since python doesnt evaluate them until we run them
# which means any unknown stuff error (eg. proto changed)
# only gets found out at runtime (annoying).
# not exhaustive, though.


class FakeMultiPath(StrEnum):
    X = "X"

    def to_int(self) -> int:
        return {self.X: 1}[self]

    def get_base_id(id: int) -> int:
        return 1


class FakeStream:
    def write(self, data: bytes) -> None:
        pass

    async def drain(self) -> None:
        pass

    async def read(self, n: int = -1) -> bytes:
        return b""


class FakeConnection:
    def __init__(self):
        stream = FakeStream()
        self.reader = stream
        self.writer = stream
        self.db = SimpleNamespace(
            lightcones=[],
            avatars={},
            relics=[],
            lineup=SimpleNamespace(overworld_lineup={}, custom_battle_lineup=None),
            scene_id=1,
            player=SimpleNamespace(name="ok", uid=1),
            multi_path=SimpleNamespace(tb_multi_path=FakeMultiPath.X),
            calyx=SimpleNamespace(
                group_id=1,
                inst_id=1,
                entity_id=1,
                prop_id=1,
                pos=SimpleNamespace(
                    x=1,
                    y=1,
                    z=1,
                ),
            ),
            global_buff=SimpleNamespace(
                castorice=True,
                sw_999=True,
                vore_override=False,
                vore_level=0,
            ),
        )
        self.freesr_data = SimpleNamespace(
            lightcones=[],
            avatars={},
            relics=[],
            battle_config=SimpleNamespace(
                battle_type=1,
                stage_id=1,
                cycle_count=1,
                custom_stats={},
                blessings=[],
                monsters=[],
            ),
        )
        self.freesr_last_modified = 0
        self.db_last_modified = 0

    async def send_packet(self, *args, **kwargs):
        pass

    def decode_packet(self, pkt, msg):
        return msg()

    async def save_db(self):
        pass

    async def refresh_freesr(self):
        pass

    async def refresh_db(self):
        pass


class FakePacket:
    def __init__(self, cmd: int = 0, head: bytes = b"", body: bytes = b""):
        self.cmd = cmd
        self.head = head
        self.body = body
