from proto.cmd import CmdRegistry
from typing import Callable, TypeVar, TYPE_CHECKING, Awaitable

if TYPE_CHECKING:
    from .connection import Connection
    from .packet import Packet

HandlerFunc = Callable[["Connection", "Packet"], Awaitable[None]]
T = TypeVar("T", bound=HandlerFunc)

HANDLER_MAP: dict[int, HandlerFunc] = {}


# example usage:
# @handler
# async def on_get_avatar_data(c: Connection, pkt: Packet) -> None:
#     pass
def handler(fn: T) -> T:
    name = fn.__name__
    if not name.startswith("on_"):
        raise ValueError(
            f"'{name}' doesn't follow 'on_something' pattern. For example, handler for GetAvatarDataCsReq should be named on_get_avatar_data."
        )

    name = "".join(part.capitalize() for part in name[3:].split("_")) + "CsReq"

    try:
        cmd_id = CmdRegistry.get_id(name)
    except ValueError as e:
        raise e

    if cmd_id in HANDLER_MAP:
        raise ValueError(f"Handler for {name} is already registered")

    HANDLER_MAP[cmd_id] = fn
    return fn


# unused import that's needed to trigger the decorators
# putting this above the decorator function will cause circular import error
from .handlers import (
    avatar,
    lineup,
    mission,
    player,
    scene,
    battle,
    item,
    archive,
    recommend,
)

DUMMY_MAP: dict[int, int] = {
    CmdRegistry.get_id(n + "CsReq"): CmdRegistry.get_id(n + "ScRsp")
    for n in [
        "GetPreAvatarGrowthInfo",
        "GetPreAvatarActivityList",
        "QueryProductInfo",
        "GetQuestData",
        "GetQuestRecord",
        "GetCurAssist",
        "GetRogueHandbookData",
        "GetDailyActiveInfo",
        "GetFightActivityData",
        "GetMultipleDropInfo",
        "GetPlayerReturnMultiDropInfo",
        "GetShareData",
        "GetTreasureDungeonActivityData",
        "PlayerReturnInfoQuery",
        "GetPlayerBoardData",
        "GetActivityScheduleConfig",
        "GetMissionData",
        "GetChallenge",
        "GetCurChallenge",
        "GetRogueInfo",
        "GetExpeditionData",
        "GetJukeboxData",
        "SyncClientResVersion",
        "DailyFirstMeetPam",
        "GetMuseumInfo",
        "GetLoginActivity",
        "GetRaidInfo",
        "GetTrialActivityData",
        "GetBoxingClubInfo",
        "GetNpcStatus",
        "TextJoinQuery",
        "GetSecretKeyInfo",
        "GetVideoVersionKey",
        "GetCurBattleInfo",
        "GetPhoneData",
        "InteractProp",
        "FinishTalkMission",
        # "GetBag",
        "PlayerLoginFinish",
        "GetFirstTalkNpc",
        "GetAssistHistory",
        "GetTrackPhotoActivityData",
        "GetSwordTrainingData",
        "GetSummonActivityData",
        "GetMainMissionCustomValue",
        "SetPlayerInfo",
        "GetPlayerDetailInfo",
        "GetGachaInfo",
        "GetFriendApplyListInfo",
        "GetChatFriendHistory",
        "GetMarkItemList",
        "RogueTournGetCurRogueCocoonInfo",
        "GetAllServerPrefsData",
        "GetRogueCommonDialogueData",
        "GetRogueEndlessActivityData",
        "RogueArcadeGetInfo",
        "ChessRogueQuery",
        "RogueTournQuery",
        "RogueMagicQuery",
        "GetBattleCollegeData",
        "GetHeartDialInfo",
        "TrainPartyGetData",
        "HeliobusActivityData",
        "GetEnteredScene",
        "GetAetherDivideInfo",
        "GetMapRotationData",
        "GetPetData",
        "EnterSection",
        "GetPamSkinData",
        "GetNpcMessageGroup",
        "GetRechargeGiftInfo",
        "GetFriendLoginInfo",
        "GetChessRogueNousStoryInfo",
        "CommonRogueQuery",
        "GetStarFightData",
        "GetAlleyInfo",
        "GetAetherDivideChallengeInfo",
        "GetOfferingInfo",
        "ClockParkGetInfo",
        "MusicRhythmData",
        "GetFightFestData",
        "DifficultyAdjustmentGetData",
        "ChimeraGetData",
        "MarbleGetData",
        "GetRechargeBenefitInfo",
        "ParkourGetData",
        "SpaceZooData",
        "GetMaterialSubmitActivityData",
        "TravelBrochureGetData",
        "RaidCollectionData",
        "GetChatEmojiList",
        "GetTelevisionActivityData",
        "GetTrainVisitorRegister",
        "GetLoginChatInfo",
        "GetFeverTimeActivityData",
        "TarotBookGetData",
        "GetMarkChest",
        # "GetArchiveData",
        "GetAllSaveRaid",
        "GetDrinkMakerData",
        "UpdateTrackMainMission",
        "GetMail",
        "GetShopList",
        "GetFriendListInfo",
        "GetFriendAssistList",
        "GetAssistList",
    ]
}

# doesnt follow pattern for some reason
DUMMY_MAP[CmdRegistry.get_id("GetLevelRewardGetListReq")] = CmdRegistry.get_id(
    "GetLevelRewardTakenListScRsp"
)
DUMMY_MAP[CmdRegistry.get_id("UpdateServerPrefsCsReq")] = CmdRegistry.get_id(
    "UpdateServerPrefsDataScRsp"
)
