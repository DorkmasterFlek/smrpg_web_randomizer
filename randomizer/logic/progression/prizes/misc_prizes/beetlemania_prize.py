from __future__ import annotations
from randomizer.data.physical_objects.bosses import (SPR0251_BEETLE_PACKET_COPY)
from randomizer.data.physical_objects.items import (BeetleObject)
from randomizer.data.variables.event_script_names import (E0161_NPC_QUEST_GRANT_BEETLEMANIA, E0162_CHEST_GRANT_BEETLEMANIA, E0218_HILL_BEETLEMANIA, E3109_FREESTANDING_BEETLEMANIA_GRANT, E3395_MIDAS_CAVE_BEETLEMANIA_GRANTER)
from randomizer.types.prize import (FortuneEnum, KeyPrize, TreasureHunterNickname, StandardPrize)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.classes import (EventScript)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import (JmpToEvent)


class BeetlemaniaPrize(StandardPrize, KeyPrize):
    _nickname = TreasureHunterNickname(
        nickname="Video Game",
        description="It's pretty addictive.",
    )
    _model = BeetleObject
    _packet_data = (SPR0251_BEETLE_PACKET_COPY, 0)
    _fortune_type: FortuneEnum = FortuneEnum.RARE

    @property
    def chest_grant(self) -> EventScript:
        return EventScript([JmpToEvent(E0162_CHEST_GRANT_BEETLEMANIA)])

    @property
    def npc_grant(self) -> EventScript:
        return EventScript([JmpToEvent(E0161_NPC_QUEST_GRANT_BEETLEMANIA)])

    @property
    def standing_grant(self) -> EventScript:
        return EventScript([JmpToEvent(E3109_FREESTANDING_BEETLEMANIA_GRANT)])

    @property
    def river_grant(self) -> EventScript:
        return EventScript([JmpToEvent(E3395_MIDAS_CAVE_BEETLEMANIA_GRANTER)])

    @property
    def hill_grant(self) -> EventScript:
        return EventScript([JmpToEvent(E0218_HILL_BEETLEMANIA)])


__all__ = ["BeetlemaniaPrize"]
