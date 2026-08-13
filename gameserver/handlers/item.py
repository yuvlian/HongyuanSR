from common.util import FreesrUtils
from proto import GetBagScRsp

from ..connection import Connection
from ..handler import handler
from ..packet import Packet


@handler
async def on_get_bag(c: Connection, pkt: Packet) -> None:
    rsp = GetBagScRsp(
        relic_list=[
            FreesrUtils.relic_to_relic_proto(relic) for relic in c.freesr_data.relics
        ],
        equipment_list=[
            FreesrUtils.lightcone_to_equipment_proto(lightcone)
            for lightcone in c.freesr_data.lightcones
        ],
    )

    await c.send_packet(rsp)
