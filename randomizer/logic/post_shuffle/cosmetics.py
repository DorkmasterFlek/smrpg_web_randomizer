"""Cosmetic settings that don't affect gameplay."""
from __future__ import annotations
from smrpgpatchbuilder.datatypes.battles.music import get_default_music
from smrpgpatchbuilder.datatypes.battle_animation_scripts.commands import PlayMusicAtVolume
import random
import os
from typing import TYPE_CHECKING, cast

from smrpgpatchbuilder.datatypes.overworld_scripts.arguments import MARIO, TOADSTOOL, BOWSER, GENO, MALLOW
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import CreatePacketAt7010, LearnSpell
from smrpgpatchbuilder.datatypes.spells.enums import Element

from randomizer.data.enemies.enemies import CZARDRAGONEnemy

from randomizer.data.packets import P094_FIRE_SPELL_CHEST, P095_BLUE_SPELL_CHEST, P096_GREEN_SPELL_CHEST, P098_GRAY_SPELL_CHEST, P097_YELLOW_SPELL_CHEST
from randomizer.logic.progression.prizes import BowserRecruitmentPrize, GenoRecruitmentPrize, MallowRecruitmentPrize, MarioRecruitmentPrize, ToadstoolRecruitmentPrize
from randomizer.data.variables.dialog_names import *
from randomizer.data.variables.screen_effect_names import SEF0004_UNKNOWN
from randomizer.logic.progression.prizelocations import BoosterTowerIndoorBossFight, FinalBossFight, MarrymoreCharacter, SeasideBeachBossFight, VolcanoExitBossFight
from randomizer.types.flags import BarrelVolcanoGate, BarrelVolcanoGating, BowsersKeepGate, BowsersKeepGating, EXPStarsAnywhere, FireworksOptions, FireworksSetting, KeepMinigameSpritesIntact, RangeFlag, SuperJump1Threshold, SuperJump2Threshold
from randomizer.types.prize import BossFightPrize, CharacterPrize, SpellPrize
from smrpgpatchbuilder.datatypes.battle_animation_scripts.commands import (
    ScreenFlashWithDuration,
    AttackTimerBegins,
    DefineObjectQueue,
    ScreenEffect,
    Pause1Frame,
    NewEffectObject,
)
from smrpgpatchbuilder.datatypes.battle_animation_scripts.arguments import NO_COLOUR
from ...types.flags import (
        CanonNames, Peach, RemakeNames, RemoveFlashes, Remake,
        ChangeNames, BossShuffleMusic, ShuffledMusic, MarioPaletteChoice,
        MallowPaletteChoice, GenoPaletteChoice, ToadstoolPaletteChoice, BowserPaletteChoice,
    )
from ...data.enemies.enemies import (
        KAMEKEnemy, BIRDETTAEnemy,
        MARIOCLONEEnemy, MARIOCLONESEnemy,
        TOADSTOOL2Enemy, TOADSTOOL3Enemy,
        BOWSERCLONEEnemy, BOWSERCOPYSEnemy,
        GENOCLONEEnemy, GENOCLONESEnemy,
        MALLOWCLONEEnemy, MALLOWCOPYSEnemy,
        PUNCHINELLOEnemy, JOHNNYEnemy, BOOSTEREnemy, BUNDTEnemy,
    )
from ...data.allies.palettes.mario import all_palettes as MARIO_PALETTES
from ...data.allies.palettes.mallow import all_palettes as MALLOW_PALETTES
from ...data.allies.palettes.geno import all_palettes as GENO_PALETTES
from ...data.allies.palettes.toadstool import all_palettes as TOADSTOOL_PALETTES
from ...data.allies.palettes.bowser import all_palettes as BOWSER_PALETTES
from ...data.minigames.star_hill_wishes import WISH_POOL, WISH_DIALOG_IDS
from ...data.variables.battle_effect_names import EF0025_PSYCH_BOMB_BG, EF0073_DUMMY
from ...types.enemy import Enemy
from ...types.item import Item
from ...types.spell import Spell
from ...types.attack import EnemyAttack
from ...types.prizelocation import BossFightLocation
from ...data.variables.dialog_names import (
        DI3847_ROOM_SERVICE_MENU,
        DI1217_SWAP_SHOP_OVER_100_POINTS,
        DI1175_SWAP_SHOP_INSTRUCTIONS,
    )
from randomizer.types.prizelocation import SpellSlotLocation

if TYPE_CHECKING:
    from ...types.gameworld import GameWorld


def apply_palette_selection(world, flag, palette_list, attr_name):
    choice = world.settings.get_flag(flag).selected
    
    if choice.name == "DEFAULT":
        return
    
    if choice.name == "RANDOM":
        setattr(world, attr_name, random.choice(palette_list))
        return
    
    for p in palette_list:
        if p.id is choice:
            setattr(world, attr_name, p)
            return


def apply_cosmetic_settings(world: GameWorld) -> None:
    """Apply cosmetic settings that don't affect gameplay.

    This configures:
    - Canon names (Kamek, Birdetta)
    - Peach name
    - Remake names for enemies, items, spells, attacks
    - Remove screen flashes (accessibility)
    - Palette swaps for characters
    - Boss shuffle music
    - Random Star Hill wishes

    Note: Cosmetics are re-seeded with current timestamp so they vary
    between generations with the same seed.
    """

    # Re-seed for cosmetics (so they vary between generations with same seed)
    # Use os.urandom for maximum entropy instead of timestamp
    random.seed(int.from_bytes(os.urandom(8), 'big'))

    if world.settings.isflag_enabled(RemakeNames):
        world.battle_dialogs.battle_dialogs[217] = " Wizakoopa’s hiding![await]"
        world.battle_dialogs.battle_dialogs[214] = 'GASSOX: Duh, huh huh...[await]'
        world.battle_dialogs.battle_dialogs[132] = ' Claymorton’s stunned!![await]'

    if world.settings.isflag_enabled(CanonNames):
        world.enemies.get_by_type(KAMEKEnemy).set_name("KAMEK")
        world.enemies.get_by_type(BIRDETTAEnemy).set_name("BIRDETTA")
        world.enemies.get_by_type(CZARDRAGONEnemy).set_name("BLARGG")
        world.battle_dialogs.battle_dialogs[217] = " Kamek’s hiding![await]"
        world.battle_dialogs.battle_dialogs[206] = 'BIRDETTA: Tee, hee![await]\n Ouch, you’re hurting me![await]\n Now it’s my turn![await]\n Get it while it’s hot![await]'

    if world.settings.isflag_enabled(Peach):
        world.allies._allies[1].name = "Peach"
        world.enemies.get_by_type(TOADSTOOL2Enemy).set_name("PEACH CLONE")
        world.enemies.get_by_type(TOADSTOOL3Enemy).set_name("PEACH CLONE S")

    # Distinguish OGs from refights when remake is enabled
    # Doesn't apply to Culex, Jinx, or Belome, they already are distinguished
    if world.settings.isflag_enabled(Remake):
        world.enemies.get_by_type(PUNCHINELLOEnemy).set_name("PUNCHINELLO 1")
        world.enemies.get_by_type(JOHNNYEnemy).set_name("JOHNNY 1")
        world.enemies.get_by_type(BOOSTEREnemy).set_name("BOOSTER 1")
        world.enemies.get_by_type(BUNDTEnemy).set_name("BUNDT 1")

    if world.settings.isflag_enabled(RemakeNames):
        world.update_dialog(DI2007_FOUND_A_BTUB_RING_AUTO_TERMINATE, '''[center]Found a “Nurture Ring”![end]''')
        world.update_dialog(DI2009_GOT_A_BTUB_RING_AWAIT_TERMINATE, '''[center]Got a “Nurture Ring”![await]''')
        for enemy in world.enemies.enemies:
            e = cast(Enemy, enemy)
            if e.remake_name is not None:
                enemy.set_name(e.remake_name)
        for item in world.items.items:
            it = cast(Item, item)
            if it.remake_name is not None:
                item.set_name(it.remake_name)
        for spell in world.spells.spells:
            sp = cast(Spell, spell)
            if sp.remake_name is not None:
                spell._title = sp.remake_name
        for attack in world.enemy_attacks.attacks:
            at = cast(EnemyAttack, attack)
            if at.remake_name is not None:
                attack.set_attack_name(at.remake_name)
        world.update_dialog(DI3072_TOWER_HENCHMAN_3_WINDOW, """SNIFSTER 3: Um...\n Nice weather we're having.[await]""")
        world.update_dialog(DI3073_TOWER_HENCHMAN_3, '''SNIFSTER 3:\n[center]You wanna fight?[await]''')
        world.overworld_dialogs.search_and_replace_in_all_dialogs("FROGFUCIUS", "FROG SAGE")
        deletables = [
            "EVENT_215_delete_vowel_1",
            "EVENT_215_delete_vowel_2",
            "EVENT_215_delete_vowel_3",
            "EVENT_160_delete_vowel_1",
            "EVENT_160_delete_vowel_2",
            "EVENT_160_delete_vowel_3",
            "EVENT_165_delete_vowel_1",
            "EVENT_165_delete_vowel_2",
            "EVENT_165_delete_vowel_3",
            "EVENT_2820_delete_vowel_1",
            "EVENT_2820_delete_vowel_2",
            "EVENT_2820_delete_vowel_3",
            "EVENT_3089_delete_vowel_1",
            "EVENT_3089_delete_vowel_2",
            "EVENT_3089_delete_vowel_3",
            "EVENT_4077L_165_delete_vowel_2",
            "EVENT_4077L_165_delete_vowel_1",
            "EVENT_4077L_165_delete_vowel_3"
        ]
        for d in deletables:
            world.event_scripts.delete_command_by_identifier(d)

    for location in world.locations.values():
        if isinstance(location, BossFightLocation) and isinstance(location.prize, BossFightPrize):
            dialogs = location.prize.get_dialog_replacements(
                remake=world.settings.isflag_enabled(RemakeNames),
                canon=world.settings.isflag_enabled(CanonNames),
                mandatory_fights_changed=not world.settings.isflag_enabled(KeepMinigameSpritesIntact),
                peach=world.settings.isflag_enabled(Peach)
                )
            for dialog_id in location._dialogs_expecting_replacement:
                if dialog_id in dialogs:
                    world.update_dialog(dialog_id, dialogs[dialog_id])
                        

    # Remove screen flashes (accessibility)
    if world.settings.isflag_enabled(RemoveFlashes):
        screenflashes = [
            "screen_flash_1",  # thunderbolt
            "screen_flash_2",
            "crusher_screenflash",  # crusher
            "darkstar_flash",  # dark star
            "spikedlink_flash_1",
            "spikedlink_flash_2",
            "spikedlink_flash_3",
        ]
        for identifier in screenflashes:
            world.battle_animations[0x35].get_command_by_name(identifier).set_colour(  # type: ignore
                NO_COLOUR
            )

        replace_screen_effects = [
            "command_0x35BE52",  # geno flash
            "geno_blast_effect",  # geno blast
            "corona_flash",
            "shaker_delete_3",
        ]
        for identifier in replace_screen_effects:
            world.battle_animations[0x35].replace_command_by_name(identifier, ScreenEffect(SEF0004_UNKNOWN, identifier=identifier))

        deletes = [
            "shaker_delete_1",  # shaker / silver bullet
            "shaker_delete_2",
            "shaker_delete_4",
            "shaker_delete_5",
            "statice_delete_1",
            "statice_delete_2",
            "statice_delete_3",
            "statice_delete_4",
            "statice_delete_5",
            "meteorswarm_delete_maybe",
            "rockcandy_delete",
            "rockcandy_delete_2",
            "geno_blast_sfx"
        ]
        for identifier in deletes:
            world.battle_animations[0x35].delete_command_by_name(identifier)
            
        blank_effects = [
            "icebomb_explosion",
            "meteorswarm_replace",  # meteor swarm
            "rockcandy_replace",  # rock candy
            "meteorblast_replace",  # meteor blast
        ]
        for identifier in blank_effects:
            world.battle_animations[0x35].get_command_by_name(
                identifier, NewEffectObject
            ).set_effect(EF0073_DUMMY)

        world.battle_animations[0x35].get_command_by_name(
            "bigbang_flash"
        ).set_effect(EF0025_PSYCH_BOMB_BG)  # type: ignore
        world.battle_animations[0x35].get_command_by_name(
            "firebomb_explosion"
        ).set_effect(EF0025_PSYCH_BOMB_BG)  # type: ignore
        world.battle_animations[0x35].replace_command_by_name(
            "command_0x35358A",
            Pause1Frame(identifier="command_0x35358A"),  # shaker / silver bullet
        )
        # statice keeps a real flash rather than a blanked effect: the deletes above
        # strip its whole Layer3On / FadeOutObject / Layer3Off scaffold, so this is
        # the only thing left holding the attack's duration.
        world.battle_animations[0x35].replace_command_by_name(
            "statice_flash", ScreenFlashWithDuration(NO_COLOUR, 44, identifier="statice_flash")  # static e!
        )

        for i in range(1, 11):
            flash_id = f"screenflash_{i}"
            world.event_scripts.delete_command_by_identifier(flash_id)

    # Palette selections (applied when non-default palette is chosen)
    apply_palette_selection(world, MarioPaletteChoice, MARIO_PALETTES, "mario_palette")
    apply_palette_selection(world, MallowPaletteChoice, MALLOW_PALETTES, "mallow_palette")
    apply_palette_selection(world, GenoPaletteChoice, GENO_PALETTES, "geno_palette")
    apply_palette_selection(world, BowserPaletteChoice, BOWSER_PALETTES, "bowser_palette")
    apply_palette_selection(world, ToadstoolPaletteChoice, TOADSTOOL_PALETTES, "toadstool_palette")

    if world.settings.isflag_enabled(ChangeNames):
        # Only rename characters and their clones if the palette has a name change.
        # Palettes with rename_character=False keep vanilla clone names (e.g. "MARIO CLONE")
        # instead of producing blanks like " CLONE".
        if world.mario_palette.rename_character:
            world.allies._allies[0].name = world.mario_palette.name
            world.enemies.get_by_type(MARIOCLONEEnemy).set_name(
                world.mario_palette.clone_name
            )
            world.enemies.get_by_type(MARIOCLONESEnemy).set_name(
                world.mario_palette.strong_clone_name
            )
            world.overworld_dialogs.search_and_replace_in_all_dialogs("MARIO CLONE", world.mario_palette.clone_name)
            world.overworld_dialogs.search_and_replace_in_all_dialogs("MARIO CLONE S", world.mario_palette.strong_clone_name)
        if world.toadstool_palette.rename_character:
            world.allies._allies[1].name = world.toadstool_palette.name
            world.enemies.get_by_type(TOADSTOOL2Enemy).set_name(
                world.toadstool_palette.clone_name
            )
            world.enemies.get_by_type(TOADSTOOL3Enemy).set_name(
                world.toadstool_palette.strong_clone_name
            )
            world.overworld_dialogs.search_and_replace_in_all_dialogs("TOADSTOOL 2", world.toadstool_palette.clone_name)
            world.overworld_dialogs.search_and_replace_in_all_dialogs("PEACH CLONE", world.toadstool_palette.clone_name)
            world.overworld_dialogs.search_and_replace_in_all_dialogs("TOADSTOOL 3", world.toadstool_palette.strong_clone_name)
            world.overworld_dialogs.search_and_replace_in_all_dialogs("S PEACH CLONE", world.toadstool_palette.strong_clone_name)
        if world.bowser_palette.rename_character:
            world.allies._allies[2].name = world.bowser_palette.name
            world.battle_dialogs.battle_dialogs[129] = f' {world.bowser_palette.name}’s mood has affected[await]\n the monster![await]\n The monster’s confused!![await]'
            world.battle_dialogs.battle_dialogs[130] = f' {world.bowser_palette.name}’s scaring the monster![await]'
            world.enemies.get_by_type(BOWSERCLONEEnemy).set_name(
                world.bowser_palette.clone_name
            )
            world.enemies.get_by_type(BOWSERCOPYSEnemy).set_name(
                world.bowser_palette.strong_clone_name
            )
            world.overworld_dialogs.search_and_replace_in_all_dialogs("BOWSER CLONE", world.bowser_palette.clone_name)
            world.overworld_dialogs.search_and_replace_in_all_dialogs("BOWSER COPY S", world.bowser_palette.strong_clone_name)
        if world.geno_palette.rename_character:
            world.allies._allies[3].name = world.geno_palette.name
            world.enemies.get_by_type(GENOCLONEEnemy).set_name(
                world.geno_palette.clone_name
            )
            world.enemies.get_by_type(GENOCLONESEnemy).set_name(
                world.geno_palette.strong_clone_name
            )
            world.overworld_dialogs.search_and_replace_in_all_dialogs("GENO CLONE", world.geno_palette.clone_name)
            world.overworld_dialogs.search_and_replace_in_all_dialogs("GENO CLONE S", world.geno_palette.strong_clone_name)
        if world.mallow_palette.rename_character:
            world.allies._allies[4].name = world.mallow_palette.name
            world.enemies.get_by_type(MALLOWCLONEEnemy).set_name(
                world.mallow_palette.clone_name
            )
            world.enemies.get_by_type(MALLOWCOPYSEnemy).set_name(
                world.mallow_palette.strong_clone_name
            )
            world.overworld_dialogs.search_and_replace_in_all_dialogs("MALLOW CLONE", world.mallow_palette.clone_name)
            world.overworld_dialogs.search_and_replace_in_all_dialogs("MALLOW COPY S", world.mallow_palette.strong_clone_name)

    world.selected_music_ids = []

    if world.settings.isflag_enabled(BossShuffleMusic):
        enabled_tracks = world.settings.get_flag(ShuffledMusic).enabled

        # Pick 8 random music IDs from the enabled tracks (with replacement if needed)
        if len(enabled_tracks) >= 8:
            selected_tracks = random.sample(enabled_tracks, 8)
        else:
            selected_tracks = random.choices(enabled_tracks, k=8)

        world.selected_music_ids = [track.music_id for track in selected_tracks]

        music_instances = get_default_music()

        # Assign random music to every battle formation (not just boss fights)
        for pack in world.battle_packs.packs:
            for formation in pack.formations:
                formation.set_music(random.choice(music_instances))

        # Randomize Smithy 2 phase transition music (battle animation script)
        smithy_2_cmd = world.get_battle_animation_command_by_name("smithy_2_music")
        assert isinstance(smithy_2_cmd, PlayMusicAtVolume)
        smithy_2_cmd.set_music(random.choice(enabled_tracks).music_id)

    # Random Star Hill wishes (truly random, not tied to seed)
    wishes = zip(WISH_DIALOG_IDS, random.sample(WISH_POOL, len(WISH_DIALOG_IDS)))
    for dialog_id, wish in wishes:
        world.update_dialog(dialog_id, wish)

    # Room service and bomb shop dialog text (depends on RemakeNames setting)

    use_remake = world.settings.isflag_enabled(RemakeNames)

    if world.room_service_items:
        low_item = cast(Item, world.get_item(world.room_service_items[0]))
        high_item = cast(Item, world.get_item(world.room_service_items[1]))
        low_price = world.room_service_prices[0] if world.room_service_prices else None
        high_price = world.room_service_prices[1] if world.room_service_prices else None
        world.update_dialog(
            DI3847_ROOM_SERVICE_MENU,
            f"[page]\n Here is the menu.[await]\n"
            f" [select]  {low_item.text_shop_menu(use_remake, low_price)}\n"
            f" [select]  {high_item.text_shop_menu(use_remake, high_price)}\n"
            f" [select]  (No thanks)[await]"
        )

    if world.bomb_shop_items:
        bomb_items = [cast(Item, world.get_item(b)) for b in world.bomb_shop_items]
        bombs = [b.name for b in bomb_items]
        world.update_dialog(
            DI1217_SWAP_SHOP_OVER_100_POINTS,
            f" If we total that up, you've got\n [0x7000] points![await][page]\n"
            f" You have more than 100 points,\n so go ahead and choose an item.[await][page]\n"
            f"  [select]  ({bombs[0]})\n"
            f"  [select]  ({bombs[1]})\n"
            f"  [select]  ({bombs[2]})[await]"
        )
        world.update_dialog(
            DI1175_SWAP_SHOP_INSTRUCTIONS,
            f"\n  Bring your unwanted items here![await][page]\n"
            f"  We'll exchange your Mushrooms\n       and Syrups for points.[await]\n"
            f"        For every 100 points\n    you'll get an item in return![await][page]\n"
            f"           You can choose\n     one of the following gifts\n"
            f"       to take away with you.[await][page]\n"
            f"  1)\"{bombs[0]}\"\n"
            f"  2)\"{bombs[1]}\"\n"
            f"  3)\"{bombs[2]}\"[await]"
        )

    world.overworld_dialogs.search_and_replace_in_all_dialogs("`MARIO_NAME`", world.allies._allies[0].name)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`PEACH_NAME`", world.allies._allies[1].name)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`BOWSER_NAME`", world.allies._allies[2].name)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`GENO_NAME`", world.allies._allies[3].name)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`MALLOW_NAME`", world.allies._allies[4].name)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`PEACH_ARTICLE`", "n" if world.allies._allies[1].name[0].lower() in "aeiou" else "")
    oc = world.overworld_character.ally
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`MAIN_CHARACTER_NAME`", world.allies._allies[oc.index].name)
    nm = world.overworld_character.name_props
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`MAIN_CHARACTER_GENDER`", nm.gender)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`MAIN_CHARACTER_GENDER_CASUAL`", nm.gender_casual)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`MAIN_CHARACTER_HONORIFIC`", nm.honorific)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`MAIN_CHARACTER_HONORIFIC_CAP`", nm.honorific.capitalize())
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`MAIN_CHARACTER_TITLE`", nm.title)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`MAIN_CHARACTER_TITLE_SHORT`", nm.title_short)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`MAIN_CHARACTER_MOLE_GREETING`", nm.mole_greeting)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`MAIN_CHARACTER_MBOY_GREETING`", nm.mboy_greeting)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`PLAYER_INSULT`", nm.insult)

    towerboss = world.get_location(BoosterTowerIndoorBossFight).prize
    assert isinstance(towerboss, BossFightPrize)
    towerboss_name = towerboss.name(
        world.settings.isflag_enabled(RemakeNames),
        world.settings.isflag_enabled(CanonNames),
    )
    towerboss_gender = towerboss.gender
    # we're not including any randomized ship dialogs when the recruited character is canonically a kid
    chapelchar = world.get_location(MarrymoreCharacter).prize
    if isinstance(chapelchar, CharacterPrize) and chapelchar._ally.index == 4:
        world.update_dialog(DI2112_RAZ_OCCUPIED, "RAZ: If there's one thing I know about `MARRYMORE_CHARACTER`, it's that he ALWAYS cries at weddings.[await] The kid can barely make it through a rehearsal without blubbering.")
        world.update_dialog(DI2114_MARRYMORE_BOSS_NAMES, " `TOWER_BOSS_1`'s fiance had something come up last minute. `TOWER_BOSS_1_GENDER_SUBJECTIVE` almost had to cancel the rehearsal.[await][page]\n It's nice that `MARRYMORE_CHARACTER` is stepping in to help carry it out.[await]")
        world.update_dialog(DI2115_MARRYMORE_SHITPOST, " Does anyone here even know who `TOWER_BOSS_1`'s fiance is?[await][page]\n I thought it was `RANDOM_BOSS_NAME_1`, but I saw `RANDOM_BOSS_GENDER_1_OBJECTIVE` visiting Yo'ster Isle with `RANDOM_BOSS_NAME_4`...[await]")
        world.update_dialog(DI2117_MARRYMORE_SHITPOST, " I'm not even invited to the wedding. I just needed to go for a walk.[await] My Discord has been full of drama since one guy posted ship art of `RANDOM_CHARACTER_NAME` and `RANDOM_BOSS_NAME_5`.[await]")
        world.update_dialog(DI2119_MARRYMORE_SHITPOST, " I heard that `TOWER_BOSS_1` proposed at a gas station. Who DOES that?![await]")

    world.overworld_dialogs.search_and_replace_in_all_dialogs("`TOWER_BOSS_1`", towerboss_name)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`TOWER_BOSS_1_GENDER_POSSESSIVE`", towerboss_gender[2])
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`TOWER_BOSS_1_GENDER_SUBJECTIVE`", towerboss_gender[0].title())
    
    cc_name = world.allies._allies[chapelchar._ally.index].name if isinstance(chapelchar, CharacterPrize) else "Toad"
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`MARRYMORE_CHARACTER`", cc_name)
    mallow_name = world.allies._allies[4].name  # Mallow is always index 4
    cc_name_pool = [n for n in
                    [*[world.allies._allies[i].name for i in range(len(world.allies._allies))], "Toad"]
        if n != cc_name and n != mallow_name
    ]
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`RANDOM_CHARACTER_NAME`", random.choice(cc_name_pool))


    bossfight_pool = [cast(BossFightPrize, l.prize) for l in world.locations.values() if isinstance(l, BossFightLocation) and isinstance(l.prize, BossFightPrize)]
    boss_pool = list(dict.fromkeys([(x.marrymore_name(
        world.settings.isflag_enabled(RemakeNames),
        world.settings.isflag_enabled(CanonNames),
    ), x.marrymore_gender) for x in bossfight_pool]))
    random_boss_names = random.sample([n for n in boss_pool  if n[0] != towerboss_name], k=5)
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`RANDOM_BOSS_NAME_1`", random_boss_names[0][0])
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`RANDOM_BOSS_NAME_2`", random_boss_names[1][0])
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`RANDOM_BOSS_NAME_3`", random_boss_names[2][0])
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`RANDOM_BOSS_NAME_4`", random_boss_names[3][0])
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`RANDOM_BOSS_NAME_5`", random_boss_names[4][0])
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`RANDOM_BOSS_GENDER_1_OBJECTIVE`", random_boss_names[0][1][1])

    sjc1 = cast(RangeFlag, world.settings.get_flag(SuperJump1Threshold)).value
    sjc2 = cast(RangeFlag, world.settings.get_flag(SuperJump2Threshold)).value
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`SUPER_JUMP_PRIZE_1_CAP`", str(sjc1))
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`SUPER_JUMP_PRIZE_2_CAP`", str(sjc2))
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`FIREWORKS_CLAUSE`", "Aren't those in Moleville?" if world.settings.is_flag_value(FireworksSetting, FireworksOptions.VANILLA) else "I wonder where you could find one?")
    if (world.settings.is_flag_value(FireworksSetting, FireworksOptions.PROGRESSIVE)):
        world.overworld_dialogs.replace_dialog(DI1296_PURTEND_STORE_NEED_FIREWORKS, " If ya bring me a “Fireworks”, then\n I\u2019ll give you a present.")

    # Bowser's Keep access
    keep_cond = world.settings.get_flag(BowsersKeepGate).selected
    if keep_cond == BowsersKeepGating.AXEM:
        world.overworld_dialogs.search_and_replace_in_all_dialogs("`BOWSERS_KEEP_CONDITION`", "with the Axem Rangers\u2019 permission.")
    elif keep_cond == BowsersKeepGating.OPEN:
        world.overworld_dialogs.search_and_replace_in_all_dialogs("`BOWSERS_KEEP_CONDITION`", "on foot.")
    elif keep_cond == BowsersKeepGating.STAR_6:
        world.overworld_dialogs.search_and_replace_in_all_dialogs("`BOWSERS_KEEP_CONDITION`", "with six Star Pieces.")
    else:
        world.overworld_dialogs.search_and_replace_in_all_dialogs("`BOWSERS_KEEP_CONDITION`", "through the volcano.")

    volcano_cond = world.settings.get_flag(BarrelVolcanoGate).selected
    if volcano_cond == BarrelVolcanoGating.NIMBUS:
        world.overworld_dialogs.search_and_replace_in_all_dialogs("`VOLCANO_CONDITION`", "while the castle is occupied by\n invaders, we\u2019re under strict\n orders to forbid entry.")
    elif volcano_cond == BarrelVolcanoGating.VALENTINA:
        world.overworld_dialogs.search_and_replace_in_all_dialogs("`VOLCANO_CONDITION`", "you need Valentina\u2019s\n permission to enter.")

    # Seaside letter
    seasideboss = world.get_location(SeasideBeachBossFight).prize
    assert isinstance(seasideboss, BossFightPrize)
    seasideboss_name = seasideboss.seaside_letter_name_if_seaside_boss(
        world.settings.isflag_enabled(RemakeNames),
        world.settings.isflag_enabled(CanonNames),
    )
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`SEASIDE_BOSS`", seasideboss_name)

    volcanoboss = world.get_location(VolcanoExitBossFight).prize
    assert isinstance(volcanoboss, BossFightPrize)
    volcanoboss_name = volcanoboss.seaside_letter_name_if_volcano_boss(
        world.settings.isflag_enabled(RemakeNames),
        world.settings.isflag_enabled(CanonNames),
    )
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`VOLCANO_BOSS_DESCRIPTION`", volcanoboss_name)

    finalboss = world.get_location(FinalBossFight).prize
    assert isinstance(finalboss, BossFightPrize)
    finalboss_name = finalboss.seaside_letter_name_if_final_boss(
        world.settings.isflag_enabled(RemakeNames),
        world.settings.isflag_enabled(CanonNames),
    )
    world.overworld_dialogs.search_and_replace_in_all_dialogs("`FINAL_BOSS_NAME`", finalboss_name)

    if world.settings.isflag_enabled(EXPStarsAnywhere):
        world.update_dialog(DI1222_SHAMAN_SALESMAN_NOT_ENOUGH_COINS, ''' I have an item to sell, but you
 don't have enough coins.[await]''')
        world.update_dialog(DI1223_SHAMAN_SALESMAN_400_COINS, ''' You're looking for items?
 I'll sell one for 400 coins.
 Are you interested?[await]
  [select] (Yes)
  [select] (No)[await]''')
        world.update_dialog(DI1224_SHAMAN_SALESMAN_2ND_PROMPT, ''' You want a better item?[await]
  [select] (Yes)
  [select] (No)[await]''')
        world.update_dialog(
DI1227_SHAMAN_SALESMAN_800_COINS, ''' I found an incredible item.
 I'll sell it for 800 coins.[await]
  [select] (Buy it)
  [select] (Pass)[await]''')
        
    # Apply spell shuffler results to dialogs and chest packets, but use the character names and spell names as per cosmetics settings
    for location in world.locations.values():
        p = location.prize
        if isinstance(p, SpellPrize):
            idx = p.spell().index
            spell = world.spells.spells[idx]
            dialog_id = p.dialog_id
            dialog_id_2 = p.autoterm_dialog_id
            world.overworld_dialogs.search_and_replace_in_all_dialogs(f"`SPELL_{p.placement_id}`", spell.title)

            char_type = p.character
            if char_type is None and isinstance(location, SpellSlotLocation):
                # For SpellSlotLocations, determine character from location class name
                loc_name = type(location).__name__
                if loc_name.startswith("Mario"):
                    char_type = MarioRecruitmentPrize
                elif loc_name.startswith("Mallow"):
                    char_type = MallowRecruitmentPrize
                elif loc_name.startswith("Geno"):
                    char_type = GenoRecruitmentPrize
                elif loc_name.startswith("Bowser"):
                    char_type = BowserRecruitmentPrize
                elif loc_name.startswith("Toadstool"):
                    char_type = ToadstoolRecruitmentPrize

            if char_type is MarioRecruitmentPrize:
                character = world.allies._allies[0]
                for c in p.character_replacement_ids + [
                    _pc + "_PKT"
                    for _pc in p.character_replacement_ids
                    if _pc.startswith("freestanding")
                ]:
                    world.event_scripts.get_command_by_identifier(c, LearnSpell).set_character(MARIO)
                world.overworld_dialogs.search_and_replace_in_dialog(dialog_id, "`CHARACTER`", character.name)
                world.overworld_dialogs.search_and_replace_in_dialog(dialog_id_2, "`CHARACTER`", character.name)
            elif char_type is ToadstoolRecruitmentPrize:
                character = world.allies._allies[1]
                for c in p.character_replacement_ids + [
                    _pc + "_PKT"
                    for _pc in p.character_replacement_ids
                    if _pc.startswith("freestanding")
                ]:
                    world.event_scripts.get_command_by_identifier(c, LearnSpell).set_character(TOADSTOOL)
                world.overworld_dialogs.search_and_replace_in_dialog(dialog_id, "`CHARACTER`", character.name)
                world.overworld_dialogs.search_and_replace_in_dialog(dialog_id_2, "`CHARACTER`", character.name)
            elif char_type is BowserRecruitmentPrize:
                character = world.allies._allies[2]
                for c in p.character_replacement_ids + [
                    _pc + "_PKT"
                    for _pc in p.character_replacement_ids
                    if _pc.startswith("freestanding")
                ]:
                    world.event_scripts.get_command_by_identifier(c, LearnSpell).set_character(BOWSER)
                world.overworld_dialogs.search_and_replace_in_dialog(dialog_id, "`CHARACTER`", character.name)
                world.overworld_dialogs.search_and_replace_in_dialog(dialog_id_2, "`CHARACTER`", character.name)
            elif char_type is GenoRecruitmentPrize:
                character = world.allies._allies[3]
                for c in p.character_replacement_ids + [
                    _pc + "_PKT"
                    for _pc in p.character_replacement_ids
                    if _pc.startswith("freestanding")
                ]:
                    world.event_scripts.get_command_by_identifier(c, LearnSpell).set_character(GENO)
                world.overworld_dialogs.search_and_replace_in_dialog(dialog_id, "`CHARACTER`", character.name)
                world.overworld_dialogs.search_and_replace_in_dialog(dialog_id_2, "`CHARACTER`", character.name)
            elif char_type is MallowRecruitmentPrize:
                character = world.allies._allies[4]
                for c in p.character_replacement_ids + [
                    _pc + "_PKT"
                    for _pc in p.character_replacement_ids
                    if _pc.startswith("freestanding")
                ]:
                    world.event_scripts.get_command_by_identifier(c, LearnSpell).set_character(MALLOW)
                world.overworld_dialogs.search_and_replace_in_dialog(dialog_id, "`CHARACTER`", character.name)
                world.overworld_dialogs.search_and_replace_in_dialog(dialog_id_2, "`CHARACTER`", character.name)
            else:
                raise Exception(f"No character assigned for spell prize {spell} at location {location}")
            for i in p.packet_replacement_ids:
                if spell.element == Element.FIRE:
                    world.event_scripts.get_command_by_identifier(i, CreatePacketAt7010).set_packet_id(P094_FIRE_SPELL_CHEST)
                elif spell.element == Element.THUNDER:
                    world.event_scripts.get_command_by_identifier(i, CreatePacketAt7010).set_packet_id(P097_YELLOW_SPELL_CHEST)
                elif spell.element == Element.ICE:
                    world.event_scripts.get_command_by_identifier(i, CreatePacketAt7010).set_packet_id(P095_BLUE_SPELL_CHEST)
                elif spell.element == Element.JUMP:
                    world.event_scripts.get_command_by_identifier(i, CreatePacketAt7010).set_packet_id(P096_GREEN_SPELL_CHEST)
                else:
                     world.event_scripts.get_command_by_identifier(i, CreatePacketAt7010).set_packet_id(P098_GRAY_SPELL_CHEST)


    

    # Restore seed for any further operations
    random.seed(world.seed)
