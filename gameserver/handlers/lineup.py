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
        for slot, avatar_id in list(d.lineup.overworld_lineup.items())
    ]

    if len(avatars) > 4:
        avatars = avatars[:4]

    return LineupInfo(
        is_virtual=False,
        plane_id=d.scene_id,
        name="Yoshihide",
        mp=0,
        max_mp=5,
        index=0,
        extra_lineup_type=ExtraLineupType.LINEUP_NONE,
        avatar_list=avatars,
        leader_slot=0,
    )


async def refresh_lineup(c: Connection) -> None:
    await c.save_db()
    await c.send_packet(SyncLineupNotify(lineup=build_lineup(c.db), reason_list=[]))


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
        name=req.name,
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

    for slot, aid in c.db.lineup.overworld_lineup.items():
        if aid == req.base_avatar_id:
            del c.db.lineup.overworld_lineup[slot]
            break

    await refresh_lineup(c)
    await c.send_packet(rsp)


@handler
async def on_join_lineup(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, JoinLineupCsReq)
    rsp = JoinLineupScRsp()

    if req.base_avatar_id in c.db.lineup.overworld_lineup.values():
        await c.send_packet(rsp)
        return

    if req.slot not in c.db.lineup.overworld_lineup:
        c.db.lineup.overworld_lineup[req.slot] = req.base_avatar_id
    else:
        for i in range(4):
            if i not in c.db.lineup.overworld_lineup:
                c.db.lineup.overworld_lineup[i] = req.base_avatar_id
                break

    await refresh_lineup(c)
    await c.send_packet(rsp)


@handler
async def on_replace_lineup(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, ReplaceLineupCsReq)
    rsp = ReplaceLineupScRsp()
    new_lineup = {}

    for avatar in req.lineup_slot_list:
        slot = avatar.slot
        if slot > 3:
            continue
        avatar_id = MultiPath.get_base_id(avatar.id)
        if avatar_id in new_lineup.values():
            continue
        new_lineup[slot] = avatar_id

    if not new_lineup:
        await c.send_packet(rsp)
        return

    c.db.lineup.overworld_lineup = new_lineup

    await refresh_lineup(c)
    await c.send_packet(rsp)
