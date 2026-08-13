import asyncio
from collections.abc import Awaitable, Callable

from proto.cmd import CmdRegistry

from .connection import Connection
from .faker import FakeConnection, FakeMultiPath, FakePacket, FakeStream
from .packet import Packet

HandlerFunc = Callable[[Connection, Packet], Awaitable[None]]

HANDLER_MAP: dict[int, HandlerFunc] = {}
DUMMY_MAP: dict[int, int] = {}


# example usage:
# @handler
# async def on_get_avatar_data(c: Connection, pkt: Packet) -> None:
#     pass
def handler[T: HandlerFunc](fn: T) -> T:
    name = fn.__name__
    if not name.startswith("on_"):
        raise ValueError(
            f"'{name}' doesn't follow 'on_something' pattern. For example, handler for GetAvatarDataCsReq should be named on_get_avatar_data."
        )

    base_name = "".join(part.capitalize() for part in name[3:].split("_"))
    cs_req_name = base_name + "CsReq"

    cmd_id = CmdRegistry.get_id(cs_req_name)

    if cmd_id in HANDLER_MAP:
        raise ValueError(f"Handler for {cs_req_name} is already registered")

    HANDLER_MAP[cmd_id] = fn

    try:
        sc_rsp_name = base_name + "ScRsp"
        DUMMY_MAP[cmd_id] = CmdRegistry.get_id(sc_rsp_name)
    except ValueError:
        pass

    conn = FakeConnection()
    packet = FakePacket(cmd=cmd_id)

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(fn(conn, packet))
    except RuntimeError:
        asyncio.run(fn(conn, packet))

    return fn


# unused import that's needed to trigger the decorators
# putting this above the decorator function will cause circular import error
from .handlers import (
    archive,
    avatar,
    battle,
    extra,
    item,
    lineup,
    mission,
    player,
    recommend,
    scene,
)


def dummy_init():
    for n in [
        "GetLevelRewardTakenList",
        "QueryProductInfo",
        "GetQuestData",
        "GetQuestRecord",
        "GetCurAssist",
        "GetDailyActiveInfo",
        "GetFightActivityData",
        "GetPlayerBoardData",
        "GetActivityScheduleConfig",
        "GetMissionData",
        "GetChallenge",
        "GetCurChallenge",
        "GetExpeditionData",
        "GetJukeboxData",
        "SyncClientResVersion",
        "GetLoginActivity",
        "GetRaidInfo",
        "GetTrialActivityData",
        "GetNpcStatus",
        "GetSecretKeyInfo",
        "GetVideoVersionKey",
        "GetCurBattleInfo",
        "GetPhoneData",
        "InteractProp",
        "FinishTalkMission",
        "GetRechargeGiftInfo",
        "GetPreAvatarGrowthInfo",
        "GetPreAvatarActivityList",
        "GetFriendAssistList",
        "GetAssistList",
        "B51RacingGetData",
    ]:
        try:
            DUMMY_MAP[CmdRegistry.get_id(n + "CsReq")] = CmdRegistry.get_id(n + "ScRsp")
        except ValueError:
            print(n)


dummy_init()

# doesnt follow pattern for some reason
# DUMMY_MAP[CmdRegistry.get_id("UpdateServerPrefsCsReq")] = CmdRegistry.get_id(
#     "UpdateServerPrefsDataScRsp"
# )
