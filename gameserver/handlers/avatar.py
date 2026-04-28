import time
from proto import (
    GetAvatarDataScRsp,
    Avatar,
    AvatarPathData,
    AvatarPathSkillTree,
)
from ..handler import handler
from ..connection import Connection
from ..packet import Packet
from common.db import MultiPath
from common.util import FreesrUtils


@handler
async def on_get_avatar_data(c: Connection, pkt: Packet) -> None:
    t = int(time.time() * 1000)
    rsp = GetAvatarDataScRsp(
        is_get_all=True,
        avatar_path_data_info_list=[
            AvatarPathData(
                unlock_timestamp=t,
                avatar_id=8002,
                rank=6,
                avatar_path_skill_tree=[
                    AvatarPathSkillTree(
                        point_id=i,
                        level=1,
                    )
                    for i in range(1, 10)
                ],
                unk_enhanced_id=0,
            )
        ],
    )

    lightcone_uid_by_avatar = {
        lc.equip_avatar: lc.internal_uid for lc in c.freesr_data.lightcones
    }

    relics_by_avatar = {
        avatar: [
            FreesrUtils.relic_to_equip_relic_proto(relic)
            for relic in c.freesr_data.relics
            if relic.equip_avatar == avatar
        ]
        for avatar in {relic.equip_avatar for relic in c.freesr_data.relics}
    }

    rsp.avatar_list = [
        Avatar(
            base_avatar_id=MultiPath.get_base_id(av.avatar_id),
            level=av.level,
            promotion=av.promotion,
            first_met_time_stamp=1712924677,
            cur_multi_path_avatar_type=av.avatar_id,
            equipment_unique_id=lightcone_uid_by_avatar.get(av.avatar_id, 0),
            has_taken_promotion_reward_list=[1, 3, 5],
        )
        for av in c.freesr_data.avatars.values()
    ]

    rsp.avatar_path_data_info_list = [
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
            unlock_timestamp=0,
            dressed_skin_id=0,
        )
        for av in c.freesr_data.avatars.values()
    ]

    await c.send_packet(rsp)
