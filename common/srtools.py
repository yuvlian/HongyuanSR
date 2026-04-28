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


class Blessing(BaseModel):
    level: int
    id: int


class Monster(BaseModel):
    monster_id: int
    amount: int
    level: int


class BattleConfig(BaseModel):
    battle_type: Optional[str] = None
    blessings: List[Blessing]
    custom_stats: List[SubAffix]
    monsters: List[List[Monster]]
    stage_id: int
    path_resonance_id: int
    cycle_count: int


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
                    relic_id=55001,
                    main_affix_id=1,
                    relic_set_id=550,
                    sub_affixes=[
                        SubAffix(
                            count=1,
                            step=3,
                            sub_affix_id=101,
                        ),
                        SubAffix(
                            count=1,
                            step=2,
                            sub_affix_id=102,
                        ),
                    ],
                )
            ],
            lightcones=[
                Lightcone(
                    equip_avatar=1001,
                    internal_uid=10001,
                    item_id=20000,
                    level=80,
                    promotion=6,
                    rank=5,
                )
            ],
            battle_config=BattleConfig(
                battle_type="Memory",
                blessings=[
                    Blessing(
                        id=1201,
                        level=1,
                    ),
                    Blessing(
                        id=1202,
                        level=1,
                    ),
                ],
                custom_stats=[
                    SubAffix(
                        count=2,
                        step=3,
                        sub_affix_id=101,
                    )
                ],
                monsters=[
                    [
                        Monster(
                            monster_id=100001,
                            amount=2,
                            level=95,
                        )
                    ],
                    [
                        Monster(
                            monster_id=100002,
                            amount=1,
                            level=98,
                        )
                    ],
                ],
                stage_id=101,
                path_resonance_id=1200,
                cycle_count=30,
            ),
            loadout=[
                Loadout(
                    name="Default",
                    avatar_id=1001,
                    relic_list=[
                        "55001",
                    ],
                )
            ],
        )
