from proto import (
    ChangeLineupLeaderCsReq,
    ChangeLineupLeaderScRsp,
    GetAllLineupDataScRsp,
    GetCurLineupDataScRsp,
    SetLineupNameCsReq,
    SetLineupNameScRsp,
    JoinLineupCsReq,
    JoinLineupScRsp,
    QuitLineupCsReq,
    QuitLineupScRsp,
    ReplaceLineupCsReq,
    ReplaceLineupScRsp,
    # SwapLineupCsReq,
    # SwapLineupScRsp,
    SyncLineupNotify,
    LineupInfo,
    LineupAvatar,
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
    MotionInfo,
    Vector,
)
from ..handler import handler
from ..connection import Connection
from ..packet import Packet
from common.db import MultiPath, DB


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
        mp=5,
        max_mp=5,
        index=0,
        extra_lineup_type=ExtraLineupType.LINEUP_NONE,
        avatar_list=avatars,
        leader_slot=0,
    )


async def refresh_lineup(c: Connection) -> None:
    await c.save_db()

    lineup = build_lineup(c.db)
    await c.send_packet(SyncLineupNotify(lineup=lineup, reason_list=[]))

    new_entities = []
    for i in range(4):        
        if avatar_id := c.db.lineup.overworld_lineup.get(i):
            new_entities.append(
                SceneEntityRefreshInfo(
                    add_entity=SceneEntityInfo(
                        entity_id=i + 1,
                        group_id=0,
                        inst_id=0,
                        actor=SceneActorInfo(
                            avatar_type=AvatarType.AVATAR_FORMAL_TYPE,
                            base_avatar_id=MultiPath.get_base_id(avatar_id),
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
            )
        else:
            new_entities.append(
                SceneEntityRefreshInfo(
                    delete_entity=i + 1
                )
            )

    await c.send_packet(
        SceneGroupRefreshScNotify(
            group_refresh_list=[
                GroupRefreshInfo(
                    group_id=0,
                    state=0,
                    refresh_type=SceneGroupRefreshType.LOADED,
                    refresh_entity=new_entities,
                )
            ],
            floor_id=(c.db.scene_id * 1000) + 1,
            dimension_id=0,
        )
    )


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
    req = c.decode_packet(pkt, QuitLineupCsReq)
    rsp = QuitLineupScRsp(
        retcode=0,
        base_avatar_id=req.base_avatar_id,
        plane_id=req.plane_id,
        is_virtual=req.is_virtual,
    )

    new_lineup_list = []
    found = False
    for aid in c.db.lineup.overworld_lineup.values():
        if aid == req.base_avatar_id:
            found = True
            continue
        new_lineup_list.append(aid)

    if found:
        c.db.lineup.overworld_lineup = {i: aid for i, aid in enumerate(new_lineup_list)}
        await refresh_lineup(c)

    await c.send_packet(rsp)


@handler
async def on_join_lineup(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, JoinLineupCsReq)
    rsp = JoinLineupScRsp()

    if req.base_avatar_id in c.db.lineup.overworld_lineup.values():
        await c.send_packet(rsp)
        return

    if len(c.db.lineup.overworld_lineup) >= 4:
        await c.send_packet(rsp)
        return

    lineup = dict(c.db.lineup.overworld_lineup)
    
    target_slot = req.slot
    if target_slot > 3 or target_slot in lineup:
        for i in range(4):
            if i not in lineup:
                target_slot = i
                break
        else:
            await c.send_packet(rsp)
            return

    lineup[target_slot] = req.base_avatar_id
    sorted_lineup = [lineup[i] for i in sorted(lineup.keys())]
    c.db.lineup.overworld_lineup = {i: aid for i, aid in enumerate(sorted_lineup)}

    await refresh_lineup(c)
    await c.send_packet(rsp)


@handler
async def on_replace_lineup(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, ReplaceLineupCsReq)
    rsp = ReplaceLineupScRsp()
    
    new_lineup = {}
    slots = sorted(req.lineup_slot_list, key=lambda x: x.slot)

    idx = 0
    added_ids = set()
    for slot_data in slots:
        if idx >= 4:
            break
        avatar_id = MultiPath.get_base_id(slot_data.id)
        if avatar_id in added_ids:
            continue
        new_lineup[idx] = avatar_id
        added_ids.add(avatar_id)
        idx += 1

    if not new_lineup:
        await c.send_packet(rsp)
        return

    c.db.lineup.overworld_lineup = new_lineup

    await refresh_lineup(c)
    await c.send_packet(rsp)
