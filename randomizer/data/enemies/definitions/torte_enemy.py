from randomizer.data.items.items import (MushroomItem)
from randomizer.types.enemy import (Enemy)
from smrpgpatchbuilder.datatypes.enemies.enums import (
    ApproachSound,
    CoinSprite,
    EntranceStyle,
    FlowerBonusType,
    HitSound,
)
from smrpgpatchbuilder.datatypes.spells.enums import (Status)


class TORTEEnemy(Enemy):
    """TORTE enemy class"""
    _monster_id: int = 142
    _name: str = "TORTE"

    _hp: int = 100
    _fp: int = 100
    _attack: int = 60
    _defense: int = 20 # changed from vanilla to match raspberry, defense is irrelevant in boss fight but matters in henchmen fights
    _magic_attack: int = 8
    _magic_defense: int = 27
    _speed: int = 99
    _evade: int = 0
    _magic_evade: int = 0
    _status_immunities: list[Status] = [Status.MUTE, Status.SLEEP, Status.POISON, Status.FEAR]
    _xp: int = 0
    _coins: int = 0
    _yoshi_cookie_item = MushroomItem
    _flower_bonus_type: FlowerBonusType = FlowerBonusType.ATTACK_UP
    _flower_bonus_chance: int = 20
    _sound_on_hit: HitSound = HitSound.KNOCK
    _sound_on_approach: ApproachSound = ApproachSound.TORTE
    _coin_sprite: CoinSprite = CoinSprite.NONE
    _entrance_style: EntranceStyle = EntranceStyle.NONE
    _cursor_x: int = 1
    _cursor_y: int = 3
    _ohko_immune: bool = True
    _psychopath_message: str = " Cake! Vatch zee CAKE.[await]"


__all__ = ["TORTEEnemy"]
