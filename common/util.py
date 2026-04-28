import aiofiles
import proto
from . import srtools as srt
from pathlib import Path
from typing import Protocol, Tuple, TypeVar, Type
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class AsyncFs:
    @staticmethod
    async def read_to_str(path: str) -> str:
        async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
            return await f.read()

    @staticmethod
    async def write_to_file(path: str, content: str) -> None:
        async with aiofiles.open(path, mode="w", encoding="utf-8") as f:
            await f.write(content)

    @staticmethod
    async def json_parse_or_write(
        path: str,
        model_type: Type[T],
        default: T,
        overwrite_invalid: bool,
    ) -> Tuple[T, bool]:
        if not Path(path).exists():
            await AsyncFs.write_to_file(
                path,
                default.model_dump_json(indent=2),
            )
            return default, True

        try:
            raw = await AsyncFs.read_to_str(path)
            return model_type.model_validate_json(raw), False

        except Exception:
            if overwrite_invalid:
                await AsyncFs.write_to_file(
                    path,
                    default.model_dump_json(indent=2),
                )
                return default, True
            raise


class SyncFs:
    # @staticmethod
    # def read_to_str(path: str) -> str:
    #     return Path(path).read_text()

    # @staticmethod
    # def write_to_file(path: str, content: str) -> None:
    #     Path(path).write_text(content)

    @staticmethod
    def get_last_modified_time(path: str) -> int:
        return int(Path(path).stat().st_mtime)


class Display(Protocol):
    def __str__(self) -> str: ...


class Log:
    @staticmethod
    def error(c: Display | str) -> None:
        print(f"ERROR: {c}")

    @staticmethod
    def info(c: Display | str) -> None:
        print(f"INFO: {c}")

    @staticmethod
    def warn(c: Display | str) -> None:
        print(f"WARN: {c}")

    @staticmethod
    def debug(c: Display | str) -> None:
        print(f"DEBUG: {c}")


class FreesrUtils:
    @staticmethod
    def get_relic_slot(relic: srt.Relic) -> int:
        return relic.relic_id % 10

    @staticmethod
    def subaffix_to_relic_affix(sub: srt.SubAffix) -> proto.RelicAffix:
        return proto.RelicAffix(
            affix_id=sub.sub_affix_id,
            cnt=sub.count,
            step=sub.step,
        )

    @staticmethod
    def relic_to_relic_proto(relic: srt.Relic) -> proto.Relic:
        return proto.Relic(
            dress_avatar_id=relic.equip_avatar,
            exp=0,
            is_protected=False,
            level=relic.level,
            main_affix_id=relic.main_affix_id,
            tid=relic.relic_id,
            unique_id=relic.internal_uid,
            sub_affix_list=[
                FreesrUtils.subaffix_to_relic_affix(sub) for sub in relic.sub_affixes
            ],
        )

    @staticmethod
    def relic_to_battle_relic_proto(relic: srt.Relic) -> proto.BattleRelic:
        return proto.BattleRelic(
            id=relic.relic_id,
            level=relic.level,
            main_affix_id=relic.main_affix_id,
            unique_id=relic.internal_uid,
            sub_affix_list=[
                FreesrUtils.subaffix_to_relic_affix(sub) for sub in relic.sub_affixes
            ],
        )

    @staticmethod
    def relic_to_equip_relic_proto(relic: srt.Relic) -> proto.EquipRelic:
        return proto.EquipRelic(
            type=FreesrUtils.get_relic_slot(relic),
            relic_unique_id=relic.internal_uid,
        )

    @staticmethod
    def lightcone_to_equipment_proto(lc: srt.Lightcone) -> proto.Equipment:
        return proto.Equipment(
            dress_avatar_id=lc.equip_avatar,
            exp=0,
            is_protected=False,
            level=lc.level,
            promotion=lc.promotion,
            rank=lc.rank,
            tid=lc.item_id,
            unique_id=lc.internal_uid,
        )

    @staticmethod
    def lightcone_to_battle_equipment_proto(lc: srt.Lightcone) -> proto.BattleEquipment:
        return proto.BattleEquipment(
            id=lc.item_id,
            level=lc.level,
            promotion=lc.promotion,
            rank=lc.rank,
        )
