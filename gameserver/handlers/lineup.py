import asyncio
import datetime
from pathlib import Path

import aiofiles

from common.db import DB
from common.util import Log
from proto import (
    AvatarType,
    ChangeLineupLeaderCsReq,
    ChangeLineupLeaderScRsp,
    ExtraLineupType,
    GetAllLineupDataScRsp,
    GetCurLineupDataScRsp,
    GroupRefreshInfo,
    JoinLineupCsReq,
    JoinLineupScRsp,
    LineupAvatar,
    LineupInfo,
    QuitLineupScRsp,
    ReplaceLineupCsReq,
    ReplaceLineupScRsp,
    SceneActorInfo,
    SceneEntityInfo,
    SceneEntityRefreshInfo,
    SceneGroupRefreshScNotify,
    SceneGroupRefreshType,
    SpBarInfo,
    SyncLineupNotify,
)

from ..connection import Connection
from ..handler import handler
from ..packet import Packet

LINEUP_LOG = Path(__file__).resolve().parents[2] / "lineup.log"
_log_lock = asyncio.Lock()


def _fmt_slots(d: DB) -> str:
    return " ".join(f"{s}:{v}" for s, v in d.lineup.overworld_lineup.items())


def _fmt_info(info: LineupInfo) -> str:
    avatars = ",".join(
        f"{a.slot}:{a.id}(hp{a.hp},cur{a.sp_bar.cur_sp})" for a in info.avatar_list
    )
    return (
        f"name={info.name} mp={info.mp}/{info.max_mp} "
        f"plane={info.plane_id} virtual={info.is_virtual} avatars=[{avatars}]"
    )


async def _log_lineup(c: Connection, event: str, detail: str = "") -> None:
    ts = datetime.datetime.now(datetime.UTC).strftime("%H:%M:%S.%f")[:-3]
    uid = f"uid={c.db.player.uid}" if c is not None and c.db else "uid=?"
    line = f"[{ts}] {uid} {event}"
    if detail:
        line += f" | {detail}"
    try:
        async with _log_lock, aiofiles.open(LINEUP_LOG, "a", encoding="utf-8") as fh:
            await fh.write(line + "\n")
    except Exception as e:  # noqa: BLE001
        Log.error(f"lineup log failed: {e}")


def build_lineup(d: DB) -> LineupInfo:
    avatars = [
        LineupAvatar(
            hp=10000,
            id=avatar_id,
            slot=slot,
            satiety=100,
            sp_bar=SpBarInfo(
                cur_sp=10000,
                max_sp=10000,
            ),
            avatar_type=AvatarType.AvatarType_AvatarFormalType,
        )
        for slot, avatar_id in d.lineup.overworld_lineup.items()
        if 0 <= slot < 4 and avatar_id
    ]

    return LineupInfo(
        name="Squad 1",
        mp=5,
        max_mp=5,
        extra_lineup_type=ExtraLineupType.ExtraLineupType_LineupNone,
        avatar_list=avatars,
        is_virtual=False,
        plane_id=0,
        leader_slot=0,
        index=0,
    )


async def refresh_lineup(c: Connection) -> None:
    new_entities = [
        SceneEntityRefreshInfo(
            add_entity=SceneEntityInfo(
                actor=SceneActorInfo(
                    uid=c.db.player.uid,
                    avatar_type=AvatarType.AvatarType_AvatarFormalType,
                    base_avatar_id=v,
                    map_layer=0,
                ),
                entity_id=k + 1,
                group_id=0,
                inst_id=0,
            )
        )
        for k, v in c.db.lineup.overworld_lineup.items()
    ]

    lineup = build_lineup(c.db)
    # await _log_lineup(
    #     c,
    #     "refresh_lineup",
    #     f"entities=[{','.join(str(e.add_entity.actor.base_avatar_id) for e in new_entities)}] "
    #     + _fmt_info(lineup),
    # )

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
    await c.send_packet(SyncLineupNotify(lineup=lineup, reason_list=[]))
    asyncio.create_task(c.save_db())


@handler
async def on_get_all_lineup_data(c: Connection, pkt: Packet) -> None:
    lineup = build_lineup(c.db)
    # await _log_lineup(c, "get_all_lineup_data", _fmt_info(lineup))
    rsp = GetAllLineupDataScRsp(
        cur_index=0,
        lineup_list=[lineup],
    )

    await c.send_packet(rsp)


@handler
async def on_get_cur_lineup_data(c: Connection, pkt: Packet) -> None:
    lineup = build_lineup(c.db)
    # await _log_lineup(c, "get_cur_lineup_data", _fmt_info(lineup))
    rsp = GetCurLineupDataScRsp(lineup=lineup)

    await c.send_packet(rsp)


@handler
async def on_join_lineup(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, JoinLineupCsReq)
    rsp = JoinLineupScRsp()

    c.db.lineup.overworld_lineup[req.slot] = req.base_avatar_id
    # await _log_lineup(
    #     c,
    #     "join_lineup",
    #     f"slot={req.slot} id={req.base_avatar_id} -> {_fmt_slots(c.db)}",
    # )
    await refresh_lineup(c)
    await c.send_packet(rsp)


@handler
async def on_replace_lineup(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, ReplaceLineupCsReq)
    rsp = ReplaceLineupScRsp()

    for slot in c.db.lineup.overworld_lineup:
        if 0 <= slot < len(req.lineup_slot_list):
            c.db.lineup.overworld_lineup[slot] = req.lineup_slot_list[slot].id
        else:
            c.db.lineup.overworld_lineup[slot] = 0

    # await _log_lineup(
    #     c,
    #     "replace_lineup",
    #     f"req=[{','.join(str(s.id) for s in req.lineup_slot_list)}] "
    #     f"-> {_fmt_slots(c.db)}",
    # )
    await refresh_lineup(c)
    await c.send_packet(rsp)


@handler
async def on_quit_lineup(c: Connection, pkt: Packet) -> None:
    # await _log_lineup(c, "quit_lineup", _fmt_slots(c.db))
    await c.send_packet(QuitLineupScRsp())


@handler
async def on_change_lineup_leader(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, ChangeLineupLeaderCsReq)
    rsp = ChangeLineupLeaderScRsp(slot=req.slot)
    # await _log_lineup(c, "change_lineup_leader", f"slot={req.slot}")

    await c.send_packet(rsp)
