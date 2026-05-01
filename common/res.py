from typing import List, Dict
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from .util import AsyncFs

FILE_DIR = "./common/res"


class AvatarConfig(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    weakness_buff_id: int
    technique_buff_ids: List[int]


class AvatarConfigs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    avatar_configs: Dict[int, AvatarConfig]


AVATAR_CONFIGS: Dict[int, AvatarConfig] = {}
_loaded = False


async def load_res():
    global _loaded
    if not _loaded:
        k, _ = await AsyncFs.json_parse_or_write(
            f"{FILE_DIR}/avatarConfigs.json",
            AvatarConfigs,
            AvatarConfigs(avatar_configs={}),
            False,
        )
        AVATAR_CONFIGS.update(k.avatar_configs)
        _loaded = True
