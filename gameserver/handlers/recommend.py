from proto import GetBigDataAllRecommendCsReq, GetBigDataAllRecommendScRsp
from ..handler import handler
from ..connection import Connection
from ..packet import Packet


@handler
async def on_get_big_data_all_recommend(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, GetBigDataAllRecommendCsReq)
    rsp = GetBigDataAllRecommendScRsp(
        big_data_recommend_type=req.big_data_recommend_type
    )

    await c.send_packet(rsp)
