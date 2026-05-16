import time
from proto import (
    ClientDownloadData,
    PlayerGetTokenScRsp,
    PlayerHeartBeatCsReq,
    PlayerHeartBeatScRsp,
    PlayerLoginScRsp,
    PlayerBasicInfo,
    GetBasicInfoScRsp,
    SetSignatureCsReq,
    SetSignatureScRsp,
    PlayerSettingInfo,
    GetPlayerBoardDataScRsp,
    HeadFrameInfo,
    DisplayAvatarVec,
    HeadIconData,
)
from ..handler import handler
from ..connection import Connection
from ..packet import Packet
from common.util import AsyncFs, Log
from collections import OrderedDict
import asyncio


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
                        except Exception as e:
                            Log.warn(f"failed to update main.lua: {e}")
    except FileNotFoundError:
        pass
    except Exception as e:
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
        signature="三生縁分 三千世界 三世因果",
        current_head_icon_id=200143,
        unlocked_head_icon_list=[
            HeadIconData(id=200143),
            HeadIconData(id=200001),
        ],
        head_frame_info=HeadFrameInfo(
            head_frame_item_id=226004,
            head_frame_expire_time=int(time.time() * 1000) + 86400000,
        ),
        current_personal_card_id=253001,
        unlocked_personal_card_list=[253001],
        display_avatar_vec=DisplayAvatarVec(is_display=False),
    )

    await c.send_packet(rsp)


@handler
async def on_set_signature(c: Connection, pkt: Packet) -> None:
    # TODO: impl tb/m7 path commands. need to fix lineup stuff first... so lazy.
    # NOTE: max len of signature is 50 bytes
    req = c.decode_packet(pkt, SetSignatureCsReq)
    string = req.signature.lower()

    # tb path
    if string.startswith("tb"):
        pass

    # march path
    elif string.startswith("m7"):
        pass

    # castorice global buff
    # example usages:
    #    gb cast on
    #    gb cast off
    elif string.startswith("gb cast"):
        new_value = "1" in string or "on" in string or "true" in string

        if c.db.global_buff.castorice != new_value:
            c.db.global_buff.castorice = new_value
            asyncio.create_task(c.save_db())

    # sw999 global buff
    # example usages:
    #    gb sw on
    #    gb sw off
    elif string.startswith("gb sw"):
        new_value = "1" in string or "on" in string or "true" in string

        if c.db.global_buff.sw_999 != new_value:
            c.db.global_buff.sw_999 = new_value
            asyncio.create_task(c.save_db())

    # custom battle lineup
    # example usages:
    #    cl clear
    #    cl add 1001
    #    cl add 1001 1002 1003
    elif string.startswith("cl"):
        parts = string.split()

        if len(parts) < 2:
            return

        if parts[1] == "clear":
            c.db.lineup.custom_battle_lineup = None
            asyncio.create_task(c.save_db())

        elif parts[1] == "add" and len(parts) > 2:
            lineup = c.db.lineup.custom_battle_lineup or OrderedDict()
            for avatar_id_str in parts[2:]:
                try:
                    avatar_id = int(avatar_id_str)
                    next_idx = max(lineup.keys()) + 1 if lineup else 0
                    lineup[next_idx] = avatar_id
                except ValueError:
                    continue
            c.db.lineup.custom_battle_lineup = lineup
            asyncio.create_task(c.save_db())

    rsp = SetSignatureScRsp(signature="三生縁分 三千世界 三世因果")
    await c.send_packet(rsp)
