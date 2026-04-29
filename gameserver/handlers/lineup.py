from proto import (
    ChangeLineupLeaderCsReq,
    ChangeLineupLeaderScRsp,
    GetAllLineupDataScRsp,
    GetCurLineupDataScRsp,
    GetLineupAvatarDataScRsp,
    SetLineupNameCsReq,
    SetLineupNameScRsp,
    JoinLineupCsReq,
    JoinLineupScRsp,
    # QuitLineupCsReq,
    QuitLineupScRsp,
    ReplaceLineupCsReq,
    ReplaceLineupScRsp,
    # SwapLineupCsReq,
    # SwapLineupScRsp,
    SyncLineupNotify,
    LineupInfo,
    LineupAvatar,
    LineupAvatarData,
    # LineupSlotData,
    ExtraLineupType,
    SpBarInfo,
    AvatarType,
    SceneGroupRefreshScNotify,
    GroupRefreshInfo,
    SceneGroupRefreshType,
    SceneEntityRefreshInfo,
    SceneEntityInfo,
    SceneActorInfo,
)
from ..handler import handler
from ..connection import Connection
from ..packet import Packet
from common.db import MultiPath, DB
import asyncio


def build_lineup(d: DB) -> LineupInfo:
    avatars = [
        LineupAvatar(
            hp=10000,
            id=MultiPath.get_base_id(avatar_id),
            slot=slot,
            sp_bar=SpBarInfo(
                max_sp=10000,
            ),
            avatar_type=AvatarType.AVATAR_FORMAL_TYPE,
        )
        for slot, avatar_id in d.lineup.overworld_lineup.items()
    ]

    # if len(avatars) > 4:
    #     avatars = avatars[:4]

    return LineupInfo(
        is_virtual=False,
        plane_id=d.scene_id,
        name="Yoshihide",
        mp=0,  # technique points. dont want people to ask why some techniques break game.
        max_mp=5,
        index=0,
        extra_lineup_type=ExtraLineupType.LINEUP_NONE,
        avatar_list=avatars,
        leader_slot=0,
    )


async def refresh_lineup(c: Connection) -> None:
    new_entities = [
        SceneEntityRefreshInfo(
            add_entity=SceneEntityInfo(
                actor=SceneActorInfo(
                    uid=c.db.player.uid,
                    avatar_type=AvatarType.AVATAR_FORMAL_TYPE,
                    base_avatar_id=MultiPath.get_base_id(v),
                ),
                entity_id=k + 1,
            )
        )
        for k, v in c.db.lineup.overworld_lineup.items()
    ]

    await c.send_packet(SyncLineupNotify(lineup=build_lineup(c.db)))
    await c.send_packet(
        SceneGroupRefreshScNotify(
            group_refresh_list=[
                GroupRefreshInfo(
                    refresh_type=SceneGroupRefreshType.LOADED,
                    refresh_entity=new_entities,
                )
            ],
            floor_id=(c.db.scene_id * 1000) + 1,
        )
    )
    asyncio.create_task(c.save_db())


@handler
async def on_change_lineup_leader(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, ChangeLineupLeaderCsReq)
    rsp = ChangeLineupLeaderScRsp(slot=req.slot)

    await c.send_packet(rsp)


@handler
async def on_get_all_lineup_data(c: Connection, pkt: Packet) -> None:
    rsp = GetAllLineupDataScRsp(
        cur_index=0,
        lineup_list=[build_lineup(c.db)],
    )

    await c.send_packet(rsp)


@handler
async def on_get_cur_lineup_data(c: Connection, pkt: Packet) -> None:
    rsp = GetCurLineupDataScRsp(lineup=build_lineup(c.db))

    await c.send_packet(rsp)


@handler
async def on_set_lineup_name(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, SetLineupNameCsReq)
    rsp = SetLineupNameScRsp(
        index=req.index,
        name="Yoshihide",
    )

    await c.send_packet(rsp)


@handler
async def on_quit_lineup(c: Connection, pkt: Packet) -> None:
    await c.send_packet(QuitLineupScRsp())


@handler
async def on_join_lineup(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, JoinLineupCsReq)
    rsp = JoinLineupScRsp()

    c.db.lineup.overworld_lineup[req.slot] = req.base_avatar_id
    await refresh_lineup(c)
    await c.send_packet(rsp)


@handler
async def on_replace_lineup(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, ReplaceLineupCsReq)
    rsp = ReplaceLineupScRsp()

    for slot, _ in c.db.lineup.overworld_lineup.items():
        if 0 <= slot < len(req.lineup_slot_list):
            c.db.lineup.overworld_lineup[slot] = req.lineup_slot_list[slot].id
        else:
            c.db.lineup.overworld_lineup[slot] = 0

    await refresh_lineup(c)
    await c.send_packet(rsp)


@handler
async def on_get_lineup_avatar_data(c: Connection, pkt: Packet) -> None:
    rsp = GetLineupAvatarDataScRsp(
        avatar_data_list=[
            LineupAvatarData(
                id=i,
                hp=10000,
                avatar_type=AvatarType.AVATAR_FORMAL_TYPE,
            )
            for i in c.db.lineup.overworld_lineup.values()
        ]
    )

    await c.send_packet(rsp)
