# 163 - MACHINEMADEMackEnemy
# pyright: reportWildcardImportFromLibrary=false

from smrpgpatchbuilder.datatypes.monster_scripts import *
from smrpgpatchbuilder.datatypes.monster_scripts.commands import *
from smrpgpatchbuilder.datatypes.monster_scripts.arguments.types.classes import DoNothing
from ...variables.battle_event_names import *
from ...variables.battle_variable_names import *
from ...items.items import *
from ...spells.spells import *
from ...enemies.enemies import *
from ...enemy_attacks.attacks import *
from smrpgpatchbuilder.datatypes.monster_scripts.arguments import *

script = MonsterScript([
	IfVarBitsSet(BV7EE001, [0]),
	IfVarBitsClear(BV7EE001, [7]),
	SetVarBits(BV7EE001, [7]),
	RunBattleDialog(132),
	Wait1TurnandRestartScript(),
	IfTurnCounterEquals(3),
	IfVarBitsClear(BV7EE003, [7]),
	IfVarLessThan(BV7EE000, 3),
	SetVarBits(BV7EE003, [7]),
	ClearVar(BV7EE006_ATTACK_PHASE_COUNTER),
	SetUntargetable(MONSTER_1_SET),
	RunBattleEvent(BE0004_MACK_JUMPS_OUT_OF_BATTLE_OFF_SCREEN),
	Wait1TurnandRestartScript(),
	IfTurnCounterEquals(5),
	IfVarBitsClear(BV7EE003, [7]),
	IfVarBitsClear(BV7EE003, [0]),
	IfLastMonsterStanding(),
	CallTarget(MONSTER_2_CALL),
	CallTarget(MONSTER_3_CALL),
	CallTarget(MONSTER_4_CALL),
	CallTarget(MONSTER_5_CALL),
	SetVarBits(BV7EE003, [0]),
	ClearVar(BV7EE000),
	Wait1TurnandRestartScript(),
	IfVarBitsClear(BV7EE003, [7]),
	IfLastMonsterStanding(),
	CastSpell(FlameWallSpell, FlameWallSpell, FlameSpell),
	Wait1TurnandRestartScript(),
	IfVarBitsClear(BV7EE003, [7]),
	Set7EE005ToRandomNumber(upper_bound=7),
	IfVarLessThan(BV7EE005_DESIGNATED_RANDOM_NUM_VAR, 4),
	Attack(Attack13),
	ClearVar(BV7EE005_DESIGNATED_RANDOM_NUM_VAR),
	Wait1TurnandRestartScript(),
	IfVarBitsClear(BV7EE003, [7]),
	CastSpell(DoNothing, FlameSpell, FlameSpell),
	Wait1TurnandRestartScript(),
	StartCounterCommands(),
	IfHPBelow(0),
	RunObjectSequence(3),
	RemoveTarget(SELF),
	Wait1TurnandRestartScript(),
	IfTargetedByElement([Element.THUNDER]),
	SetVarBits(BV7EE001, [0]),
	Wait1TurnandRestartScript()
])