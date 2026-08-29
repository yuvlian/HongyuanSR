import asyncio
import time
from collections import OrderedDict

from common.db import MultiPath
from common.util import AsyncFs, FreesrUtils, Log
from proto import (
    AvatarPathChangedNotify,
    AvatarSkillTree,
    AvatarType,
    ClientDownloadData,
    DisplayAvatarDetailInfo,
    DisplayAvatarVec,
    GetAssistHistoryScRsp,
    GetBasicInfoScRsp,
    GetPlayerBoardDataScRsp,
    GetPlayerDetailInfoScRsp,
    HeadFrameInfo,
    HeadIconData,
    MultiPathAvatarType,
    PlatformType,
    PlayerBasicInfo,
    PlayerDetailInfo,
    PlayerGetTokenScRsp,
    PlayerHeartBeatCsReq,
    PlayerHeartBeatScRsp,
    PlayerLoginFinishScRsp,
    PlayerLoginScRsp,
    PlayerSettingInfo,
    PlayerSyncScNotify,
    SetSignatureCsReq,
    SetSignatureScRsp,
)

from ..connection import Connection
from ..handler import handler
from ..packet import Packet
from .avatar import build_avatar_sync

DEFAULT_SIGNATURE = "三生縁分 三千世界 三世因果"
MAX_SIGNATURE_BYTES = 50


@handler
async def on_player_get_token(c: Connection, pkt: Packet) -> None:
    rsp = PlayerGetTokenScRsp(
        uid=c.db.player.uid,
    )

    await c.send_packet(rsp)


@handler
async def on_player_heart_beat(c: Connection, pkt: Packet) -> None:
    t = int(time.time() * 1000)
    req = c.decode_packet(pkt, PlayerHeartBeatCsReq)
    rsp = PlayerHeartBeatScRsp(
        client_time_ms=req.client_time_ms,
        server_time_ms=t,
    )

    try:
        lua_content = await AsyncFs.read_to_str("main.lua")
        ## -- exec=XY
        ##         ↑↑
        ##         │└─ reset_after
        ##         └── should_execute
        marker = "-- exec="
        pos = lua_content.find(marker)

        if pos != -1:
            flag_pos = pos + len(marker)

            if len(lua_content) >= flag_pos + 2:
                should_execute = lua_content[flag_pos] == "t"
                reset_after = lua_content[flag_pos + 1] == "t"

                if should_execute:
                    rsp.download_data = ClientDownloadData(
                        version=51,
                        time=t,
                        data=lua_content.encode(),
                    )

                    if reset_after:
                        # tt -> ft
                        updated = (
                            lua_content[:flag_pos] + "f" + lua_content[flag_pos + 1 :]
                        )
                        try:
                            await AsyncFs.write_to_file("main.lua", updated)
                        except (OSError, ValueError) as e:
                            Log.warn(f"failed to update main.lua: {e}")
    except FileNotFoundError:
        pass
    except (OSError, ValueError) as e:
        Log.error(e)

    await c.send_packet(rsp)


@handler
async def on_player_login(c: Connection, pkt: Packet) -> None:
    t = int(time.time() * 1000)
    rsp = PlayerLoginScRsp(
        basic_info=PlayerBasicInfo(
            nickname=c.db.player.name,
            level=67,
            stamina=240,
            world_level=5,
        ),
        server_timestamp_ms=t,
        stamina=240,
    )

    await c.send_packet(rsp)


@handler
async def on_get_basic_info(c: Connection, pkt: Packet) -> None:
    gender = 2 if (c.db.multi_path.tb_multi_path.to_int() & 1) == 0 else 1
    rsp = GetBasicInfoScRsp(
        cur_day=1,
        player_setting_info=PlayerSettingInfo(),
        is_gender_set=True,
        gender=gender,
    )

    await c.send_packet(rsp)


@handler
async def on_get_player_board_data(c: Connection, pkt: Packet) -> None:
    rsp = GetPlayerBoardDataScRsp(
        signature=DEFAULT_SIGNATURE,
        current_head_icon_id=200143,
        unlocked_head_icon_list=[
            HeadIconData(id=200143),
            # HeadIconData(id=200001),
        ],
        # head_frame_info=HeadFrameInfo(
        #     head_frame_item_id=226004,
        #     head_frame_expire_time=int(time.time() * 1000) + 86400000,
        # ),
        # current_personal_card_id=253001,
        # unlocked_personal_card_list=[253001],
        display_avatar_vec=DisplayAvatarVec(is_display=False),
    )

    await c.send_packet(rsp)


@handler
async def on_get_player_detail_info(c: Connection, pkt: Packet) -> None:
    gender = 2 if (c.db.multi_path.tb_multi_path.to_int() & 1) == 0 else 1

    display = []
    for pos, a in enumerate(c.freesr_data.avatars.values()):
        if pos >= 6:
            break
        display.append(
            DisplayAvatarDetailInfo(
                avatar_id=a.avatar_id,
                avatar_type=int(AvatarType.AvatarType_AvatarFormalType),
                pos=pos,
                level=a.level,
                promotion=a.promotion,
                rank=a.data.rank,
                enhanced_id=a.enhanced_id or 0,
                dressed_skin_id=0,
                skilltree_list=[
                    AvatarSkillTree(point_id=k, level=v)
                    for k, v in a.data.skills_by_anchor_type.items()
                ],
            )
        )

    assist = display[:4] or [DisplayAvatarDetailInfo(avatar_id=1001)]
    await c.send_packet(
        GetPlayerDetailInfoScRsp(
            detail_info=PlayerDetailInfo(
                uid=c.db.player.uid,
                world_level=5,
                platform=PlatformType.PC,
                signature=DEFAULT_SIGNATURE,
                display_avatar_list=display,
                assist_avatar_list=assist,
                is_banned=False,
                level=67,
                head_icon=200143,
                nickname=c.db.player.name,
                gender=gender,
                head_frame_info=HeadFrameInfo(
                    head_frame_item_id=226004,
                    head_frame_expire_time=(int(time.time()) + 86400) * 1000,
                ),
            )
        )
    )


@handler
async def on_get_assist_history(c: Connection, pkt: Packet) -> None:
    await c.send_packet(GetAssistHistoryScRsp())


def truncate_sig(s: str) -> str:
    return s.encode("utf-8")[:MAX_SIGNATURE_BYTES].decode("utf-8", errors="ignore")


def parse_bool(args: list[str], default: bool) -> bool | None:
    if not args:
        return default
    a = args[0]
    if a in ("on", "1", "true"):
        return True
    if a in ("off", "0", "false"):
        return False
    return None


async def sync_player(c: Connection) -> None:
    await c.send_packet(
        PlayerSyncScNotify(
            del_relic_list=list(range(1, 3001)),
            del_equipment_list=list(range(3001, 3501)),
        )
    )
    await c.send_packet(
        PlayerSyncScNotify(avatar_sync=build_avatar_sync(c, equipped=False))
    )
    await c.send_packet(
        PlayerSyncScNotify(
            relic_list=[
                FreesrUtils.relic_to_relic_proto(r) for r in c.freesr_data.relics
            ],
            equipment_list=[
                FreesrUtils.lightcone_to_equipment_proto(lc)
                for lc in c.freesr_data.lightcones
            ],
        )
    )
    await c.send_packet(
        PlayerSyncScNotify(avatar_sync=build_avatar_sync(c, equipped=True))
    )


async def path_command(c: Connection, command: str, args: list[str]) -> str:
    if not args:
        return "missing id"
    is_tb = command == "tb"
    mp = MultiPath.parse(args[0])
    if mp is None:
        return f"unknown path: {truncate_sig(args[0])}"
    if is_tb and not (8001 <= mp.to_int() <= 8010):
        return "tb id must be 8001-8010"
    if not is_tb and mp not in (MultiPath.MARCH_PRESERVATION, MultiPath.MARCH_HUNT):
        return "m7 must be 1001/1224"

    if is_tb:
        if c.db.multi_path.tb_multi_path != mp:
            c.db.multi_path.tb_multi_path = mp
            asyncio.create_task(c.save_db())
        await c.send_packet(
            AvatarPathChangedNotify(
                base_avatar_id=8001,
                cur_multi_path_avatar_type=MultiPathAvatarType(mp.to_int()),
            )
        )
        await sync_player(c)
    else:
        if c.db.multi_path.march_multi_path != mp:
            c.db.multi_path.march_multi_path = mp
            asyncio.create_task(c.save_db())
        await c.send_packet(
            AvatarPathChangedNotify(
                base_avatar_id=1001,
                cur_multi_path_avatar_type=MultiPathAvatarType(mp.to_int()),
            )
        )
    return f"{command}: {mp.name.lower()}"


def lineup_command(c: Connection, args: list[str]) -> str | None:
    if len(args) < 1:
        return None
    if args[0] == "clear":
        c.db.lineup.custom_battle_lineup = None
        asyncio.create_task(c.save_db())
        return "cl cleared"
    if args[0] == "add" and len(args) > 1:
        lineup = c.db.lineup.custom_battle_lineup or OrderedDict()
        added = 0
        for avatar_id_str in args[1:]:
            try:
                avatar_id = int(avatar_id_str)
            except ValueError:
                continue
            next_idx = max(lineup.keys()) + 1 if lineup else 0
            lineup[next_idx] = avatar_id
            added += 1
        c.db.lineup.custom_battle_lineup = lineup
        asyncio.create_task(c.save_db())
        return f"cl +{added}"
    return None


@handler
async def on_set_signature(c: Connection, pkt: Packet) -> None:
    req = c.decode_packet(pkt, SetSignatureCsReq)
    parts = req.signature.lower().split()
    command = parts[0] if parts else ""
    args = parts[1:]
    feedback = None

    if command in ("tb", "m7"):
        feedback = await path_command(c, command, args)
    elif command == "gb":
        sub = args[0] if args else ""
        on = parse_bool(args[1:], True)
        if on is None:
            feedback = "gb needs on/off"
        else:
            match sub:
                case "cast":
                    if c.db.global_buff.castorice != on:
                        c.db.global_buff.castorice = on
                        asyncio.create_task(c.save_db())
                    feedback = f"castorice {'on' if on else 'off'}"
                case "sw":
                    if c.db.global_buff.sw_999 != on:
                        c.db.global_buff.sw_999 = on
                        asyncio.create_task(c.save_db())
                    feedback = f"sw {'on' if on else 'off'}"
                case _:
                    feedback = "gb needs cast/sw"
    elif command == "cl":
        feedback = lineup_command(c, args)
    elif command == "sync":
        await sync_player(c)
        feedback = "synced"

    await c.send_packet(
        SetSignatureScRsp(
            signature=truncate_sig(
                feedback if feedback is not None else DEFAULT_SIGNATURE
            )
        )
    )


@handler
async def on_player_login_finish(c: Connection, pkt: Packet) -> None:
    await c.send_packet(PlayerLoginFinishScRsp())
