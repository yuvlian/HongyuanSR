# from proto import GetCurBattleInfoScRsp, BattleEndStatus
from ..handler import handler
from ..connection import Connection
from ..packet import Packet


@handler
async def on_get_cur_battle_info(c: Connection, pkt: Packet) -> None:
    # await c.send_packet(
    #     GetCurBattleInfoScRsp(last_end_status=BattleEndStatus.BATTLE_END_QUIT)
    # )
    pass
