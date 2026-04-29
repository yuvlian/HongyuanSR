from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from .util import AsyncFs

FILE_DIR = "./common/res"

# NOTE:
# this module isn't really used,
# it's just so that if you wanna have res, you already have a skeleton for it


class AvatarConfig(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    weakness_buff_id: int
    technique_buff_ids: List[int]


class AvatarConfigs(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    avatar_configs: Dict[int, AvatarConfig]


AVATAR_CONFIGS: Optional[Dict[int, AvatarConfig]] = None


async def load_res():
    global AVATAR_CONFIGS
    if AVATAR_CONFIGS is None:
        k, _ = await AsyncFs.json_parse_or_write(
            f"{FILE_DIR}/avatarConfigs.json",
            AvatarConfigs,
            AvatarConfigs(avatar_configs={}),
            False,
        )
        AVATAR_CONFIGS = k.avatar_configs
