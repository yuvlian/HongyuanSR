from proto import (
    StartCocoonStageCsReq,
    StartCocoonStageScRsp,
    PveBattleResultCsReq,
    PveBattleResultScRsp,
    SceneBattleInfo,
    BattleBuff,
    BattleRelic,
    BattleTargetList,
    BattleTarget,
    RelicAffix,
)
from ..handler import handler
from ..connection import Connection
from ..packet import Packet
from common.res import AVATAR_CONFIGS
from common.util import FreesrUtils
from common.srtools import BattleType
from random import randint


@handler
async def on_p_v_e_battle_result(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, PveBattleResultCsReq)
    rsp = PveBattleResultScRsp(
        end_status=req.end_status,
        battle_id=req.battle_id,
    )

    await c.send_packet(rsp, override_name="PVEBattleResultScRsp")


async def create_battle_info(
    c: Connection, caster_id: int, skill_idx: int
) -> SceneBattleInfo:
    await c.refresh_freesr()
    await c.refresh_db()
    sr = c.freesr_data
    db = c.db
    battle_type = sr.battle_config.battle_type

    if battle_type == BattleType.SU:
        raise Exception("SU battle isn't supported, never will be")

    battle_info = SceneBattleInfo(
        battle_id=1,
        world_level=6,
        stage_id=sr.battle_config.stage_id,
        rounds_limit=sr.battle_config.cycle_count or 0xFFFFFFFF,
        logic_random_seed=randint(0, 0xFFFFFFFF),
    )

    lineup = db.lineup.custom_battle_lineup or db.lineup.overworld_lineup

    lightcone_by_avatar = {lc.equip_avatar: lc for lc in c.freesr_data.lightcones}

    relics_by_avatar = {
        avatar: [
            relic for relic in c.freesr_data.relics if relic.equip_avatar == avatar
        ]
        for avatar in {relic.equip_avatar for relic in c.freesr_data.relics}
    }

    dahlia_exists = False
    first_in_lineup = 0

    # battle avatars
    for aidx, aid in lineup.items():
        if first_in_lineup == 0:
            first_in_lineup = aid
        if aid == 8001:
            aid = db.multi_path.tb_multi_path.to_int()
        if aid == 1001:
            aid = db.multi_path.march_multi_path.to_int()
        if not dahlia_exists:
            dahlia_exists = aid == 1321

        if av := sr.avatars.get(aid):
            battle_av, techs = FreesrUtils.avatar_to_battle_avatar_proto(
                av, aidx, lightcone_by_avatar.get(aid), relics_by_avatar.get(aid, [])
            )

            battle_info.buff_list.extend(techs)

            if (
                caster_id > 0
                and aidx == (caster_id - 1)
                and 1000119 not in av.techniques
            ):
                if avc := AVATAR_CONFIGS.get(aid):
                    battle_info.buff_list.append(
                        BattleBuff(
                            id=avc.weakness_buff_id,
                            level=1,
                            owner_index=aidx,
                            wave_flag=0xFFFFFFFF,
                            dynamic_values={
                                "SkillIndex": float(skill_idx),
                            },
                        )
                    )

            battle_info.battle_avatar_list.append(battle_av)

            # march hunt tech hardcode
            if aid == 1224:
                battle_info.buff_list.append(
                    BattleBuff(
                        id=122401,
                        level=3,
                        wave_flag=0xFFFFFFFF,
                        owner_index=aidx,
                        dynamic_values={
                            "#ADF_1": 3.0,
                            "#ADF_2": 3.0,
                        },
                        target_index_list=[0],
                    )
                )

    # custom stats
    for stat in sr.battle_config.custom_stats:
        for i in range(len(battle_info.battle_avatar_list)):
            if len(battle_info.battle_avatar_list[i].relic_list) == 0:
                battle_info.battle_avatar_list[i].relic_list.append(
                    BattleRelic(id=61011, main_affix_id=1, level=1)
                )

            found = False
            for j in range(
                len(battle_info.battle_avatar_list[i].relic_list[0].sub_affix_list)
            ):
                if (
                    battle_info.battle_avatar_list[i]
                    .relic_list[0]
                    .sub_affix_list[j]
                    .affix_id
                    == stat.sub_affix_id
                ):
                    battle_info.battle_avatar_list[i].relic_list[0].sub_affix_list[
                        j
                    ].cnt = stat.count
                    found = True
                    break

            if not found:
                battle_info.battle_avatar_list[i].relic_list[0].sub_affix_list.append(
                    RelicAffix(
                        affix_id=stat.sub_affix_id,
                        cnt=stat.count,
                        step=stat.step,
                    )
                )

    # blessings
    for blessing in sr.battle_config.blessings:
        battle_buff = BattleBuff(
            id=blessing.id,
            level=blessing.level,
            wave_flag=0xFFFFFFFF,
            owner_index=0xFFFFFFFF,
        )

        if dk := blessing.dynamic_key:
            battle_buff.dynamic_values[dk.key] = float(dk.value)

        if dvs := blessing.dynamic_values:
            for dv in dvs:
                if dv.key not in battle_buff.dynamic_values:
                    battle_buff.dynamic_values[dv.key] = float(dv.value)

        battle_info.buff_list.append(battle_buff)

    # pf score thingy
    if battle_type == BattleType.PF:
        if battle_info.stage_id >= 30309011:
            battle_info.battle_target_info[1] = BattleTargetList(
                battle_target_list=[BattleTarget(id=10003, progress=0)]
            )
        else:
            battle_info.battle_target_info[1] = BattleTargetList(
                battle_target_list=[BattleTarget(id=10002, progress=0)]
            )

        for i in range(2, 5):
            battle_info.battle_target_info[i] = BattleTargetList()

        battle_info.battle_target_info[5] = BattleTargetList(
            battle_target_list=[
                BattleTarget(
                    id=2001,
                    progress=0,
                ),
                BattleTarget(
                    id=2002,
                    progress=0,
                ),
            ]
        )

    # apoc shadow
    if battle_type == BattleType.AS:
        battle_info.battle_target_info[1] = BattleTargetList(
            battle_target_list=[
                BattleTarget(
                    id=90005,
                    progress=0,
                )
            ]
        )

    battle_info.monster_wave_list = FreesrUtils.monsters_to_scene_monster_wave_protos(
        sr.battle_config.monsters
    )

    # hardcode some buffs for first unit in lineup & global buffs
    has_sw_global, has_castorice_global = False, False
    for i in range(0, len(battle_info.buff_list)):
        if not has_sw_global:
            has_sw_global = battle_info.buff_list[i].id == 150602
        if not has_castorice_global:
            has_castorice_global = battle_info.buff_list[i].id == 140703
        # cerydra & DHPT technique
        if (
            battle_info.buff_list[i].id == 141202
            or battle_info.buff_list[i].id == 141403
        ):
            battle_info.buff_list[i].owner_index = (
                first_in_lineup
                if first_in_lineup != 0
                else battle_info.buff_list[i].owner_index
            )
            continue
        # TODO: dance partner
        if dahlia_exists and battle_info.buff_list[i].id == 0xFFFFFFFF:
            battle_info.buff_list[i].owner_index = (
                first_in_lineup
                if first_in_lineup != 0
                else battle_info.buff_list[i].owner_index
            )

    if not has_castorice_global:
        battle_info.buff_list.append(
            BattleBuff(
                id=140703,
                level=1,
                wave_flag=0xFFFFFFFF,
                owner_index=0xFFFFFFFF,
                dynamic_values={},
            )
        )

    if not has_sw_global:
        battle_info.buff_list.append(
            BattleBuff(
                id=150602,
                level=1,
                wave_flag=0xFFFFFFFF,
                owner_index=0xFFFFFFFF,
                dynamic_values={},
            )
        )

    return battle_info


@handler
async def on_start_cocoon_stage(c: Connection, pkt: Packet) -> None:
    battle_info = await create_battle_info(c, 0, 0)
    req = c.decode_packet(pkt, StartCocoonStageCsReq)
    rsp = StartCocoonStageScRsp(
        prop_entity_id=req.prop_entity_id,
        cocoon_id=req.cocoon_id,
        wave=req.wave,
        battle_info=battle_info,
    )

    await c.send_packet(rsp)
