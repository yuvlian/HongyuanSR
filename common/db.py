from enum import StrEnum
from pydantic import BaseModel
from typing import Dict, Optional


FILE_NAME = "db.json"


class Vec3(BaseModel):
    x: int
    y: int
    z: int


class MultiPath(StrEnum):
    MARCH_PRESERVATION = "march_preservation"
    MARCH_HUNT = "march_hunt"
    CAELUS_DESTRUCTION = "caelus_destruction"
    STELLE_DESTRUCTION = "stelle_destruction"
    CAELUS_PRESERVATION = "caelus_preservation"
    STELLE_PRESERVATION = "stelle_preservation"
    CAELUS_HARMONY = "caelus_harmony"
    STELLE_HARMONY = "stelle_harmony"
    CAELUS_REMEMBRANCE = "caelus_remembrance"
    STELLE_REMEMBRANCE = "stelle_remembrance"
    CAELUS_ELATION = "caelus_elation"
    STELLE_ELATION = "stelle_elation"

    def to_int(self) -> int:
        return {
            self.MARCH_PRESERVATION: 1001,
            self.MARCH_HUNT: 1224,
            self.CAELUS_DESTRUCTION: 8001,
            self.STELLE_DESTRUCTION: 8002,
            self.CAELUS_PRESERVATION: 8003,
            self.STELLE_PRESERVATION: 8004,
            self.CAELUS_HARMONY: 8005,
            self.STELLE_HARMONY: 8006,
            self.CAELUS_REMEMBRANCE: 8007,
            self.STELLE_REMEMBRANCE: 8008,
            self.CAELUS_ELATION: 8009,
            self.STELLE_ELATION: 8010,
        }[self]

    @staticmethod
    def get_base_id(id: int) -> int:
        if id == 1224:
            return 1001
        if id < 8000:
            return id
        return 8001


class CalyxEntity(BaseModel):
    entity_id: int
    group_id: int
    inst_id: int
    prop_id: int
    pos: Vec3


class PlayerEntity(BaseModel):
    uid: int
    name: str
    map_layer: int
    pos: Vec3


class PlayerMultiPath(BaseModel):
    march_multi_path: MultiPath
    tb_multi_path: MultiPath


class PlayerLineup(BaseModel):
    overworld_lineup: Dict[int, int]
    # this overrides the overworld_lineup when entering battle
    custom_battle_lineup: Optional[Dict[int, int]] = None


class DB(BaseModel):
    scene_id: int
    calyx: Optional[CalyxEntity] = None
    player: PlayerEntity
    multi_path: PlayerMultiPath
    lineup: PlayerLineup

    @staticmethod
    def default() -> "DB":
        return DB(
            scene_id=20313,
            calyx=CalyxEntity(
                entity_id=1337,
                group_id=186,
                inst_id=300001,
                prop_id=808,
                pos=Vec3(
                    x=31440,
                    y=192020,
                    z=433790,
                ),
            ),
            player=PlayerEntity(
                uid=333,
                name="Araya",
                map_layer=2,
                pos=Vec3(
                    x=31440,
                    y=192820,
                    z=433790,
                ),
            ),
            multi_path=PlayerMultiPath(
                march_multi_path=MultiPath.MARCH_PRESERVATION,
                tb_multi_path=MultiPath.STELLE_ELATION,
            ),
            lineup=PlayerLineup(overworld_lineup={0: 1002}, custom_battle_lineup=None),
        )
