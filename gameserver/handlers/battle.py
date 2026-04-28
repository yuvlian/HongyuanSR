from proto import (
    StartCocoonStageCsReq,
    StartCocoonStageScRsp,
    PveBattleResultCsReq,
    PveBattleResultScRsp,
    SceneBattleInfo,
)
from ..handler import handler
from ..connection import Connection
from ..packet import Packet
from common.srtools import BattleType
from random import randint


@handler
def on_p_v_e_battle_result(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, PveBattleResultCsReq)
    rsp = PveBattleResultScRsp(
        end_status=req.end_status,
        battle_id=req.battle_id,
    )

    await c.send_packet(rsp)


def create_battle_info(c: Connection) -> SceneBattleInfo:
    await c.refresh_freesr()
    sr = c.freesr_data
    db = c.db

    if sr.battle_config.battle_type == BattleType.SU:
        raise Exception("SU battle isn't supported, never will be")

    battle_info = SceneBattleInfo(
        battle_id=1,
        world_level=6,
        stage_id=sr.battle_config.stage_id,
        rounds_limit=sr.battle_config.cycle_count,
        logic_random_seed=randint(0, 0xFFFFFFFF),
    )

    first_in_lineup = 0
    lineup = None

    if db.lineup.custom_battle_lineup:
        lineup = db.lineup.custom_battle_lineup
    else:
        lineup = db.lineup.overworld_lineup

    for aidx, aid in lineup.items():
        if aid == 8001:
            aid = db.multi_path.tb_multi_path.to_int()
        elif aid == 1001:
            aid = db.multi_path.march_multi_path.to_int()

        if aidx == 0:
            first_in_lineup = aid

        if av := sr.avatars.get(aid):
            pass

    return battle_info


@handler
def on_start_cocoon_stage(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, StartCocoonStageCsReq)
    rsp = StartCocoonStageScRsp(
        prop_entity_id=req.prop_entity_id,
        cocoon_id=req.cocoon_id,
        wave=req.wave,
    )

    await c.send_packet(rsp)
