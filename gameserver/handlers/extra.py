from proto import (
    GetFriendListInfoScRsp,
    GetFriendLoginInfoScRsp,
    GetGachaInfoScRsp,
    GetMailScRsp,
)

from ..connection import Connection
from ..handler import handler
from ..packet import Packet

# TODO: group these properly (eg. gacha stuff to gacha.py)


@handler
async def on_get_gacha_info(c: Connection, pkt: Packet) -> None:
    await c.send_packet(GetGachaInfoScRsp())


@handler
async def on_get_mail(c: Connection, pkt: Packet) -> None:
    await c.send_packet(GetMailScRsp(is_end=True))


@handler
async def on_get_friend_list_info(c: Connection, pkt: Packet) -> None:
    await c.send_packet(GetFriendListInfoScRsp())


@handler
async def on_get_friend_login_info(c: Connection, pkt: Packet) -> None:
    await c.send_packet(GetFriendLoginInfoScRsp())
