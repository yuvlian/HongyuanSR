import time
from proto import (
    ClientDownloadData,
    PlayerGetTokenScRsp,
    PlayerHeartBeatCsReq,
    PlayerHeartBeatScRsp,
    PlayerLoginScRsp,
    PlayerBasicInfo,
    GetBasicInfoScRsp,
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
