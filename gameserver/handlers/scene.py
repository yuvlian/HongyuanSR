from proto import (
    GetCurSceneInfoScRsp,
    SceneInfo,
    SceneEntityGroupInfo,
    SceneEntityInfo,
    SceneActorInfo,
    ScenePropInfo,
    SceneIdentifier,
    AvatarType,
    MotionInfo,
    Vector,
)
from ..handler import handler
from ..connection import Connection
from ..packet import Packet
from common.db import MultiPath


@handler
async def on_get_cur_scene_info(c: Connection, pkt: Packet) -> None:
    entity_group_list = []

    player_entities = []
    for slot, av_id in c.db.lineup.overworld_lineup.items():
        player_entities.append(
            SceneEntityInfo(
                entity_id=slot + 1,
                actor=SceneActorInfo(
                    base_avatar_id=MultiPath.get_base_id(av_id),
                    avatar_type=AvatarType.AVATAR_FORMAL_TYPE,
                    uid=c.db.player.uid,
                ),
                motion=MotionInfo(
                    pos_index=Vector(
                        x=c.db.player.pos.x,
                        y=c.db.player.pos.y,
                        z=c.db.player.pos.z,
                    ),
                    rot_index=Vector(),
                ),
            )
        )

    if player_entities:
        entity_group_list.append(
            SceneEntityGroupInfo(
                group_id=0,
                state=0,
                entity_list=player_entities,
            )
        )

    if c.db.calyx:
        entity_group_list.append(
            SceneEntityGroupInfo(
                state=1,
                group_id=c.db.calyx.group_id,
                entity_list=[
                    SceneEntityInfo(
                        group_id=c.db.calyx.group_id,
                        inst_id=c.db.calyx.inst_id,
                        entity_id=c.db.calyx.entity_id,
                        prop=ScenePropInfo(
                            prop_state=1,
                            prop_id=c.db.calyx.prop_id,
                        ),
                        motion=MotionInfo(
                            pos_index=Vector(
                                x=c.db.calyx.pos.x,
                                y=c.db.calyx.pos.y,
                                z=c.db.calyx.pos.z,
                            ),
                            rot_index=Vector(),
                        ),
                    )
                ],
            )
        )

    rsp = GetCurSceneInfoScRsp(
        scene=SceneInfo(
            plane_id=c.db.scene_id,
            entry_id=(c.db.scene_id * 100) + 1,
            floor_id=(c.db.scene_id * 1000) + 1,
            game_mode_type=1,
            leader_entity_id=1,
            entity_group_list=entity_group_list,
            scene_identifier=SceneIdentifier(floor_id=(c.db.scene_id * 1000) + 1),
        )
    )

    await c.send_packet(rsp)
