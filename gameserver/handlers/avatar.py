from common.db import MultiPath
from common.util import FreesrUtils
from proto import (
    Avatar,
    AvatarPathData,
    AvatarPathSkillTree,
    AvatarSync,
    GetAvatarDataScRsp,
    SetAvatarEnhancedIdScRsp,
    TakePromotionRewardScRsp,
)

from ..connection import Connection
from ..handler import handler
from ..packet import Packet


def build_avatar_sync(c: Connection, equipped: bool = True) -> AvatarSync:
    lightcone_uid_by_avatar = (
        {lc.equip_avatar: lc.internal_uid for lc in c.freesr_data.lightcones}
        if equipped
        else {}
    )

    avatar_list = []
    for av in c.freesr_data.avatars.values():
        base_id = MultiPath.get_base_id(av.avatar_id)
        avatar = Avatar(
            base_avatar_id=base_id,
            level=av.level,
            promotion=av.promotion,
            first_met_time_stamp=1712924677,
            equipment_unique_id=lightcone_uid_by_avatar.get(av.avatar_id, 0),
            has_taken_promotion_reward_list=[1, 3, 5],
        )

        if base_id != av.avatar_id and base_id == 8001:
            avatar.cur_multi_path_avatar_type = c.db.multi_path.tb_multi_path.to_int()
        elif base_id != av.avatar_id and base_id == 1001:
            avatar.cur_multi_path_avatar_type = (
                c.db.multi_path.march_multi_path.to_int()
            )
        else:
            avatar.cur_multi_path_avatar_type = base_id

        avatar_list.append(avatar)

    relics_by_avatar = (
        {
            avatar: [
                FreesrUtils.relic_to_equip_relic_proto(relic)
                for relic in c.freesr_data.relics
                if relic.equip_avatar == avatar
            ]
            for avatar in {relic.equip_avatar for relic in c.freesr_data.relics}
        }
        if equipped
        else {}
    )

    path_list = [
        AvatarPathData(
            avatar_id=av.avatar_id,
            rank=av.data.rank,
            equip_relic_list=relics_by_avatar.get(av.avatar_id, []),
            avatar_path_skill_tree=[
                AvatarPathSkillTree(
                    point_id=k,
                    level=v,
                )
                for k, v in av.data.skills_by_anchor_type.items()
            ],
            path_equipment_id=lightcone_uid_by_avatar.get(av.avatar_id, 0),
            unk_enhanced_id=av.enhanced_id or 0,
            unlock_timestamp=1712924677,
            dressed_skin_id=0,
        )
        for av in c.freesr_data.avatars.values()
    ]

    return AvatarSync(avatar_list=avatar_list, avatar_path_data_info_list=path_list)


@handler
async def on_get_avatar_data(c: Connection, pkt: Packet) -> None:
    sync = build_avatar_sync(c)

    rsp = GetAvatarDataScRsp(
        is_get_all=True,
        avatar_list=sync.avatar_list,
        avatar_path_data_info_list=sync.avatar_path_data_info_list,
    )

    await c.send_packet(rsp)


@handler
async def on_take_promotion_reward(c: Connection, pkt: Packet) -> None:
    await c.send_packet(TakePromotionRewardScRsp())


@handler
async def on_set_avatar_enhanced_id(c: Connection, pkt: Packet) -> None:
    await c.send_packet(SetAvatarEnhancedIdScRsp())
