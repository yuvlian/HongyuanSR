from proto import (
    GetMissionStatusCsReq,
    GetMissionStatusScRsp,
    Mission,
    MissionStatus,
)

from ..connection import Connection
from ..handler import handler
from ..packet import Packet


@handler
async def on_get_mission_status(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, GetMissionStatusCsReq)
    rsp = GetMissionStatusScRsp(
        finished_main_mission_id_list=req.main_mission_id_list,
        sub_mission_status_list=[
            Mission(id=i, progress=1, status=MissionStatus.MissionFinish)
            for i in req.sub_mission_id_list
        ],
    )

    await c.send_packet(rsp)
