from __future__ import annotations
from typing import TYPE_CHECKING
from randomizer.data.enemies.enemies import (AXEMBLACKEnemy, AXEMGREENEnemy, AXEMPINKEnemy, AXEMRANGERSEnemy, AXEMREDEnemy, AXEMYELLOWEnemy)
from randomizer.data.packs.pack_collection import (FORM0292_ONE_AXEMRANGERS_ONE_AXEMRED_ONE_AXEMBLACK_ONE_AXEMPINK_ONE_AXEMGREEN_ONE_AXEMYELLOW)
from randomizer.data.physical_objects.bosses import (AxemRedObject, AxemRedStatueObject)
from randomizer.data.physical_objects.henchmen import (AxemBlackHenchman, AxemGreenHenchman, AxemPinkHenchman, AxemYellowHenchman)
from randomizer.data.variables.battle_event_names import (BE0061_ONLY_MARIO_IS_THERE)
from randomizer.data.variables.battlefield_names import (BF39_BLADE_AXEM_RANGERS)
from randomizer.data.variables.dialog_names import (
    DI0049_NIMBUS_EGG_BOSS_TALK_AFTER_WINNING,
    DI1120_NIMBUS_BIRD_GUARD,
    DI1660_SHIP_PASSWORD_COMPLETE,
    DI1694_FINAL_SHIP_HENCHMEN_DEFEATED,
    DI1695_FINAL_SHIP_HENCHMEN_AFTER_BOSS_DEFEATED,
    DI1778_SHIP_BOSS_AFTER_DEFEAT_BEFORE_LEAVING,
    DI1779_SHIP_BOSS_AFTER_DEFEAT_MUCH_LATER,
    DI1781_SHIP_BOSS_JUMP_ON_HEAD,
    DI1782_SHIP_BOSS_DRINK,
    DI1784_SHIP_BOSS_SIDEKICK_IN_ROOM_2,
    DI1785_SHIP_BOSS_SIDEKICK_IN_ROOM_1,
    DI1786_LETTER_FROM_SHIP_BOSS,
    DI1792_SHIP_BOSS_SIDEKICK_IN_ROOM_3,
    DI1793_SHIP_BOSS_SIDEKICK_IN_ROOM_4,
    DI1945_NIMBUS_GUARD,
    DI2023_SHIP_BOSS_2_DRINK,
    DI2061_HEAD_CHEF,
    DI2062_APPRENTICE_CHEF,
    DI2180_CHAPEL_NPC,
    DI2503_NEED_X_MORE_ITEMS_MARRYMORE,
    DI2560_TOWER_HENCHMAN_1,
    DI2572_TOWER_HENCHMAN_2,
    DI2830_SEASIDE_BOSS_WELCOMES_YOU,
    DI2832_OCCUPIED_SEASIDE_INNKEEPER,
    DI2838_OCCUPIED_SEASIDE_HENCHMAN_BOSS_NAME,
    DI2847_OCCUPIED_SEASIDE_HENCHMAN_SHED_GUARD,
    DI2848_OCCUPIED_SEASIDE_HENCHMAN_SHED_GUARD,
    DI3044_DOJO_BOSS_1_AFTER_DEFEAT,
    DI3057_MONSTRO_SUPERBOSS_PROMPT,
    DI3058_MONSTRO_POSTGAME_SUPERBOSS_PROMPT,
    DI3072_TOWER_HENCHMAN_3_WINDOW,
    DI3073_TOWER_HENCHMAN_3,
    DI3338_MONSTRO_SUPERBOSS_HINT,
    DI3352_DOJO_BOSS_1_FULLY_DEFEATED,
    DI3353_DOJO_BOSS_2_FULLY_DEFEATED,
    DI4060_NEED_TO_DO_CHAPEL_CHECKS,
)
from randomizer.data.variables.variable_names import (MAP_DIRECTIONAL_BOWSERS_KEEP_GATE, MAP_DIRECTIONAL_NIMBUS_LAND_VISTA_HILL, MAP_GATE, MAP_VISTA_HILL)
from randomizer.types.prize import (BossFightHenchman, BossFightPrize)
from smrpgpatchbuilder.datatypes.battles.formations_packs.types.classes import (FormationMember)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.classes import (EventScript)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import (ClearBit, SetBit)
from randomizer.types.flags import (BowsersKeepGate, BowsersKeepGating, FactoryGate, FactoryGating)

if TYPE_CHECKING:
    from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands.types.classes import (UsableEventScriptCommand)
    from randomizer.types.gameworld import (GameWorld)


class AxemRangersBossFight(BossFightPrize):
    _text = "Axem Rangers"
    _formation = FORM0292_ONE_AXEMRANGERS_ONE_AXEMRED_ONE_AXEMBLACK_ONE_AXEMPINK_ONE_AXEMGREEN_ONE_AXEMYELLOW
    _members = [
        FormationMember(AXEMRANGERSEnemy, 201, 79),
        FormationMember(AXEMREDEnemy, 135, 111, hidden_at_start=True),
        FormationMember(AXEMBLACKEnemy, 135, 127, hidden_at_start=True),
        FormationMember(AXEMPINKEnemy, 151, 143, hidden_at_start=True),
        FormationMember(AXEMGREENEnemy, 183, 151, hidden_at_start=True),
        FormationMember(AXEMYELLOWEnemy, 215, 151, hidden_at_start=True),
    ]
    _anchor_enemy = [
        AXEMREDEnemy,
        AXEMYELLOWEnemy,
        AXEMBLACKEnemy,
        AXEMPINKEnemy,
        AXEMGREENEnemy,
    ]
    _force_start_event = BE0061_ONLY_MARIO_IS_THERE
    _force_battlefield = BF39_BLADE_AXEM_RANGERS
    _seaside_letter_name_if_seaside_boss = "the Axems"
    _seaside_letter_name_if_volcano_boss = "a huge AX flying around"
    _seaside_letter_name_if_final_boss = "the Axem Rangers' stooges."
    _seaside_letter_name_if_sunken_ship_boss = "ya boi red"

    _character_henchmen = [
        BossFightHenchman(monster=AXEMBLACKEnemy, model=AxemBlackHenchman),
        BossFightHenchman(monster=AXEMPINKEnemy, model=AxemPinkHenchman),
        BossFightHenchman(monster=AXEMYELLOWEnemy, model=AxemYellowHenchman),
        BossFightHenchman(monster=AXEMGREENEnemy, model=AxemGreenHenchman),
    ]

    _gender = ("they", "them", "their", "theirs", "themselves")
    _marrymore_name = "Axem Red"
    _marrymore_single_gender = ("he", "him", "his", "his", "himself")

    _npc_models = [AxemRedObject]
    _statue_npc = AxemRedStatueObject

    _dialog_replacements = {
        DI0049_NIMBUS_EGG_BOSS_TALK_AFTER_WINNING: """AXEM RED: We’re busy playing Uno\n in here. Go bother someone else![await]""",
        DI1660_SHIP_PASSWORD_COMPLETE: """ Listen up, nerd![delay_30] You may have\n figured out our password, but\n we’re not going down without\n a fight![await]""",
        DI1694_FINAL_SHIP_HENCHMEN_DEFEATED: """PIRATE: You’re pretty tough, `MAIN_CHARACTER_MOLE_GREETING`. All right. I’ll let you through to the Axem Rangers’ place.[await]""",
        DI1695_FINAL_SHIP_HENCHMEN_AFTER_BOSS_DEFEATED: """PIRATE: That’s AMAZING!\n No one’s EVER whipped\n the AXEM RANGERS!![await]""",
        DI1778_SHIP_BOSS_AFTER_DEFEAT_BEFORE_LEAVING: """AXEM RED: How could this happen\n to the Axem Rangers?![await]""",
        DI1779_SHIP_BOSS_AFTER_DEFEAT_MUCH_LATER: """AXEM RED: Yo! Quit wasting your\n time around here, you’ve got a\n world to save![await]""",
        DI1781_SHIP_BOSS_JUMP_ON_HEAD: """AXEM RED: Yo, `MAIN_CHARACTER_NAME`!\n This isn’t cool!\n Get off of my head.[await]""",
        DI1782_SHIP_BOSS_DRINK: """ Yo! This energy drink is preem![await]\n Axem Red Bull gives me wings![await]""",
        DI2023_SHIP_BOSS_2_DRINK: """ Yo! This energy drink is preem![await]\n Axem Red Bull gives me wings![await]""",
        DI1784_SHIP_BOSS_SIDEKICK_IN_ROOM_2: """AXEM BLACK: Red can be kind of\n a chump when he loses.[await]""",
        DI1785_SHIP_BOSS_SIDEKICK_IN_ROOM_1: """AXEM PINK: I hate it down here!\n The water makes my makeup run![await]""",
        DI1786_LETTER_FROM_SHIP_BOSS: """\n yo `MAIN_CHARACTER_NAME`,[await][page]\n hru? fite was zzz, so I went bak 2 teh ship 4 a nap. text me when ur done w/ `SEASIDE_BOSS`.[await]\n green would not shut up bout how he saw `VOLCANO_BOSS_DESCRIPTION` near teh volcano.[await]pink flirted w/ a dood from `FINAL_BOSS_NAME` wtf?[await]\n black wants 2 punk them, but yellow got the squirtz again... so we got 2 go chill 4 a bit.[await]\n Hit me bak l8r. [await][page]\n\n                                     peace\n                                        red[await]""",
        DI1792_SHIP_BOSS_SIDEKICK_IN_ROOM_3: """AXEM YELLOW: Say, do you have\n anything to eat?[await]""",
        DI1793_SHIP_BOSS_SIDEKICK_IN_ROOM_4: """AXEM GREEN: The four of them may\n be hot heads, but I truly enjoy\n causing mischief with them.[await]""",
        DI2061_HEAD_CHEF: """AXEM BLACK: Why the heck do I have to bake a cake that I’m not going to get to eat?![await]""",
        DI2062_APPRENTICE_CHEF: """AXEM PINK: Not EVERYTHING we do is evil. Today we’re baking a cake that looks like Axem Red.[await]""",
        DI2180_CHAPEL_NPC: """ Reverend Red must have gotten\n lost on his way here.""",
        DI2503_NEED_X_MORE_ITEMS_MARRYMORE: """AXEM RED: Listen! You’re not\n going anywhere until you find [0x7024]\n more of `MARRYMORE_CHARACTER`’s item(s)![await]""",
        DI4060_NEED_TO_DO_CHAPEL_CHECKS: """AXEM RED: Listen up! You’re not\n done yet! Get the rest of the items\n left in this room.[await]""",
        DI2560_TOWER_HENCHMAN_1: """SNIFIT 1: Hello there.[await]\n The Axem Rangers are busy right\n now, so they can’t play.[await][page]\n Come back some other time, or you\n can try to force your way in...[await]""",
        DI2572_TOWER_HENCHMAN_2: """SNIFIT 2: Please refrain\n from bothering the Axem Rangers.[await]""",
        DI2830_SEASIDE_BOSS_WELCOMES_YOU: """AXEM RED: Listen up![await]\n Quit snooping around town![await]""",
        DI2832_OCCUPIED_SEASIDE_INNKEEPER: """AXEM YELLOW: You tired?[await]\n I’m feeling nice today, so you can\n stay for free.[await]\n  [select] (Thanks)\n  [select] (I’ll pass)[await]""",
        DI2838_OCCUPIED_SEASIDE_HENCHMAN_BOSS_NAME: """ You will find Axem Red...\n in his house. He is...the most\n respected person here.[await]""",
        DI2847_OCCUPIED_SEASIDE_HENCHMAN_SHED_GUARD: """[center]\nAXEM BLACK: Beat it, clod![await]""",
        DI2848_OCCUPIED_SEASIDE_HENCHMAN_SHED_GUARD: """AXEM PINK: Get lost, `PLAYER_INSULT`!\n [delay]This shed belongs to the Axem\n Rangers![await]""",
        DI3044_DOJO_BOSS_1_AFTER_DEFEAT: """AXEM RED: Yo! It won’t be enough\n to win just once. The dojo master\n has three forms.[await]""",
        DI3057_MONSTRO_SUPERBOSS_PROMPT: """ Yo! What do you want?![await]\n  [select] (A fight)\n  [select] (Uh...)[await]""",
        DI3058_MONSTRO_POSTGAME_SUPERBOSS_PROMPT: """ Yo! What do you want?![await]\n  [select] (A fight)\n  [select] (Uh...)[await]""",
        DI3338_MONSTRO_SUPERBOSS_HINT: """ It’s really weird.\n Sometimes I hear the people\n next door.[await][page]\n They’re always mumbling about\n Shades-this and Makeup-that.[await][page]\n Sometimes I’d like to ask them what\n they’re babbling about, but the door\n won’t open without a Shiny Stone.[await][page]\n `FIREWORKS_CLAUSE`[await]""",
        DI3352_DOJO_BOSS_1_FULLY_DEFEATED: """[center]\nAXEM RED: I’m way outta shape![await]""",
        DI3353_DOJO_BOSS_2_FULLY_DEFEATED: """[center]\nAXEM RED: I’m way outta shape![await]""",
        DI1120_NIMBUS_BIRD_GUARD: """[center]\nAXEM PINK: Get lost, jerk![await]""", 
        DI1945_NIMBUS_GUARD: """[center]\nAXEM BLACK: Beat it, clod![await]""",
    }
    _dialog_replacements_remake = {
        DI2560_TOWER_HENCHMAN_1: """SNIFSTER 1: Hello there.[await]\n The Axem Rangers are busy right\n now, so they can’t play.[await][page]\n Come back some other time, or you\n can try to force your way in...[await]""",
        DI2572_TOWER_HENCHMAN_2: """SNIFSTER 2: Please refrain\n from bothering the Axem Rangers.[await]""",
    }
    _dialog_replacements_if_mandatory_fights_changed = {
        DI2560_TOWER_HENCHMAN_1: """AXEM BLACK: Green hasn’t shown\n up to cover me for lunch yet![await][pause] I’m\n so mad, I could fight somebody![await]""",
        DI2572_TOWER_HENCHMAN_2: """AXEM PINK: Where do you clods\n think you’re going?![await]""",
        DI3072_TOWER_HENCHMAN_3_WINDOW: """AXEM YELLOW: Man...[delay] I wish\n someone would bring me some food\n up here![await]""",
        DI3073_TOWER_HENCHMAN_3: """[center]\nAXEM YELLOW: Get lost, bub![await]""",
    }

    def boss_hunt_unlocks(self, world: GameWorld) -> EventScript:
        output: list[UsableEventScriptCommand] = []
        if world.settings.is_flag_value(
            BowsersKeepGate, BowsersKeepGating.AXEM
        ):
            output.extend(
                [
                    SetBit(MAP_VISTA_HILL),
                    ClearBit(MAP_DIRECTIONAL_NIMBUS_LAND_VISTA_HILL),
                ]
            )
            if world.settings.is_flag_value(
                FactoryGate, FactoryGating.OPEN
            ):
                output.extend(
                    [
                        SetBit(MAP_GATE),
                        SetBit(MAP_DIRECTIONAL_BOWSERS_KEEP_GATE),
                    ]
                )
        return EventScript(output)


__all__ = ["AxemRangersBossFight"]
