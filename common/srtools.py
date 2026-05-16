from enum import StrEnum
from pydantic import BaseModel
from typing import Dict, List, Optional


FILE_NAME = "freesr-data.json"


class Data(BaseModel):
    rank: int
    skills: Dict[int, int]
    skills_by_anchor_type: Dict[int, int]


class Avatar(BaseModel):
    avatar_id: int
    data: Data
    level: int
    promotion: int
    sp_max: int
    sp_value: int
    techniques: List[int]
    enhanced_id: Optional[int] = None


class DynamicKey(BaseModel):
    key: str
    value: int


class Blessing(BaseModel):
    level: int
    id: int
    dynamic_key: Optional[DynamicKey] = None
    dynamic_values: Optional[List[DynamicKey]] = None


class Monster(BaseModel):
    monster_id: int
    amount: int
    level: int
    cur_hp: Optional[int] = None
    max_hp: Optional[int] = None


class BattleType(StrEnum):
    MOC = "MOC"
    PF = "PF"
    SU = "SU"
    AS = "AS"


class BattleConfig(BaseModel):
    battle_type: Optional[BattleType] = None
    blessings: List[Blessing]
    custom_stats: List[SubAffix]
    monsters: List[List[Monster]]
    stage_id: int
    path_resonance_id: int
    cycle_count: Optional[int] = None


class Lightcone(BaseModel):
    equip_avatar: int
    internal_uid: int
    item_id: int
    level: int
    promotion: int
    rank: int


class Loadout(BaseModel):
    name: str
    avatar_id: int
    relic_list: List[str]


class SubAffix(BaseModel):
    count: int
    step: int
    sub_affix_id: int


class Relic(BaseModel):
    equip_avatar: int
    internal_uid: int
    level: int
    sub_affixes: List[SubAffix]
    relic_id: int
    main_affix_id: int
    relic_set_id: int


class FreesrData(BaseModel):
    key: str
    avatars: Dict[int, Avatar]
    relics: List[Relic]
    lightcones: List[Lightcone]
    battle_config: BattleConfig
    loadout: Optional[List[Loadout]] = None

    @staticmethod
    def default() -> "FreesrData":
        return FreesrData(
            key="default",
            avatars={
                avatar_id: Avatar(
                    avatar_id=avatar_id,
                    data=Data(
                        rank=0,
                        skills={
                            n: 1
                            for n in (
                                *range(avatar_id * 1000 + 1, avatar_id * 1000 + 5),
                                avatar_id * 1000 + 7,
                                *range(avatar_id * 1000 + 101, avatar_id * 1000 + 104),
                                *range(avatar_id * 1000 + 201, avatar_id * 1000 + 211),
                            )
                        },
                        skills_by_anchor_type={i: 1 for i in range(1, 19)},
                    ),
                    level=80,
                    promotion=6,
                    sp_max=120 if avatar_id == 1001 else 100,
                    sp_value=0,
                    techniques=[avatar_id * 100 + 1],
                )
                for avatar_id in range(1001, 1005)
            },
            relics=[
                Relic(
                    equip_avatar=1001,
                    internal_uid=1,
                    level=15,
                    relic_id=61321,
                    main_affix_id=1,
                    relic_set_id=132,
                    sub_affixes=[
                        SubAffix(
                            count=1,
                            step=2,
                            sub_affix_id=4,
                        ),
                        SubAffix(
                            count=1,
                            step=2,
                            sub_affix_id=7,
                        ),
                        SubAffix(
                            count=6,
                            step=12,
                            sub_affix_id=8,
                        ),
                        SubAffix(
                            count=1,
                            step=2,
                            sub_affix_id=9,
                        ),
                    ],
                )
            ],
            lightcones=[
                Lightcone(
                    equip_avatar=1001,
                    internal_uid=0,
                    item_id=24005,
                    level=80,
                    promotion=6,
                    rank=5,
                )
            ],
            battle_config=BattleConfig(
                battle_type="MOC",
                blessings=[
                    Blessing(
                        id=3030146,
                        level=1,
                    ),
                ],
                custom_stats=[],
                monsters=[
                    [
                        Monster(
                            monster_id=5023020,
                            amount=1,
                            level=95,
                        ),
                        Monster(
                            monster_id=5013060,
                            amount=1,
                            level=95,
                        ),
                    ],
                    [
                        Monster(
                            monster_id=5014030,
                            amount=1,
                            level=95,
                        )
                    ],
                ],
                stage_id=30123122,
                path_resonance_id=0,
                cycle_count=30,
            ),
            loadout=[],
        )
