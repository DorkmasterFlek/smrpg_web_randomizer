"""Assemble the final ROM patch from all randomized game data.

Extracted from types/gameworld.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import logging
import random
from concurrent.futures import (ThreadPoolExecutor)
from randomizer.data.credits.credits import (update_credits)
from randomizer.data.items.items import (RoyalSyrupItem)
from randomizer.data.packets.packets import (Packet)
from randomizer.data.variables.pack_names import (
    PACK055_MONSTRO_DOOR_POSTGAME,
    PACK216_MONSTRO_DOOR_BOSS,
)
from randomizer.data.variables.sprite_palette_names import (
    SPAL293_ABXY_ACTION_BUTTON_SELECTION_IN_BATTLE,
    SPAL379_ABXY_BUTTONS_FROM_BOWYER_S_BUTTON_LOCK,
)
from randomizer.logic.green_switch_glow import (get_patch as _green_switch_glow_patch)
from randomizer.logic.rom.sprite_cache import (
    SpriteCacheError,
    deserialize as deserialize_sprites,
)
from randomizer.logic.rom.sprite_reclaim import (dialog_reclaim_ranges)
from randomizer.logic.shufflers.minigames import (get_minecart_track_patch)
from randomizer.patches import (asm)
from randomizer.logic.progression.prizelocations.marios_house.starting_character1 import (
    StartingCharacter1,
)
from randomizer.types.flags import (
    BossScaleOptions,
    BossShuffleScaleStats,
    BowserPaletteChoice,
    EXPChallenge,
    EXPChallengeOptions,
    FixInvincibility,
    GenoPaletteChoice,
    HoldB,
    InfuseSpellElements,
    JapaneseABXY,
    MallowPaletteChoice,
    MarioPaletteChoice,
    RandomMinecartTrack,
    RemoveFlashes,
    ShowEquips,
    ToadstoolPaletteChoice,
    UncapMaxFP,
)
from randomizer.types.patch import (Patch)
from randomizer.types.prize import (CharacterPrize)
from randomizer.types.spell import (CharacterSpell)
from smrpgpatchbuilder.datatypes.graphics.classes import (AnimationBank)
from typing import (cast)

if TYPE_CHECKING:
    from randomizer.types.gameworld import GameWorld

logger = logging.getLogger(__name__)


def get_patch(world: GameWorld) -> Patch:
    # Return cached patch if already generated
    if world._cached_patch is not None:
        return world._cached_patch

    patch = Patch(debug_mode=world._debug_bps_patches)
    progress = 45

    # Open-mode base ROM data the randomizer does not regenerate (effect
    # animations/graphics/palettes, tilesets, and assorted gap data). This is
    # the romhack BASE LAYER: applied first so every render, flag-gated patch,
    # and palette cosmetic below overrides it where they write (e.g. no_exp
    # zeroes the EXP table; cosmetics recolor effect palettes). Only the
    # render-disjoint bytes are carried. See asm/static_data.py.
    patch.add_dict(asm.static_data.get_patch(), source="static_data")

    # Dialogue font: punctuation glyphs for the codes item names use (0x7B-0x7E).
    # Vanilla leaves them blank and static_data fills them with unused icons, so
    # an item name drawn with the dialogue font (battle spoils box, [0x70A7])
    # renders "Yoshi-Ade" as "Yoshi<snowflake>Ade".
    patch.add_dict(
        asm.dialog_font_item_punctuation.get_patch(),
        source="dialog_font_item_punctuation",
    )

    world._report_progress("Assembling battle animations...", progress)
    for animation_bank in world.battle_animations.values():
        patches = animation_bank.render()
        for p in patches:
            patch.add_data(p[0], p[1], source="battle_animations")
    progress += 3

    palette_flags = [
        MarioPaletteChoice,
        MallowPaletteChoice,
        GenoPaletteChoice,
        BowserPaletteChoice,
        ToadstoolPaletteChoice,
    ]
    if any(
        world.settings.get_flag(f).selected.name != "DEFAULT" for f in palette_flags
    ) or world.overworld_character.ally.index != 0:
        patch.add_dict(world.mario_palette.render(world), source="mario_palette")
        patch.add_dict(world.mallow_palette.render(world), source="mallow_palette")
        patch.add_dict(world.geno_palette.render(world), source="geno_palette")
        patch.add_dict(world.bowser_palette.render(world), source="bowser_palette")
        patch.add_dict(world.toadstool_palette.render(world), source="toadstool_palette")


    # Render scripts and dialogs FIRST to reclaim unused space for animations


    # Overworld glow effects hardcode the CGRAM palette row they animate, so
    # re-aim them once partitions are final and room objects reflect the
    # shuffle. See logic/green_switch_glow.py.
    patch.add_dict(_green_switch_glow_patch(world), source="green_switch_glow")

    # NOTE: render() returns pointer_table + script_content combined,
    # so we must write to pointer_table_start, not start
    for event_script_bank in world.event_scripts.banks:
        world._report_progress("Assembling event scripts...", progress)
        rendered = event_script_bank.render()
        patch.add_data(
            event_script_bank.pointer_table_start, rendered, source="event_scripts"
        )
        progress += 3

    # Overworld dialogs (rendered before sprites to reclaim unused space)
    world._report_progress("Assembling dialogs...", progress)
    dialog_data = world.overworld_dialogs.render()
    for addr, data in dialog_data.items():
        patch.add_data(addr, data, source="overworld_dialogs")
    progress += 3

    # Action scripts (rendered before sprites to reclaim unused space)
    # NOTE: render() returns pointer_table + script_content combined,
    # so we must write to pointer_table_start, not start
    world._report_progress("Assembling action scripts...", progress)
    action_data = world.action_scripts.render()
    patch.add_data(
        world.action_scripts.pointer_table_start,
        action_data,
        source="action_scripts",
    )
    progress += 3

    # Monster AI scripts (rendered before sprites to reclaim unused space)
    world._report_progress("Assembling monster AI scripts...", progress)
    monster_scripts = world.monster_scripts.render()
    patch.add_data(
        world.monster_scripts.pointer_table_start,
        monster_scripts[0],
        source="monster_scripts",
    )
    patch.add_data(
        world.monster_scripts.range_2_start,
        monster_scripts[1],
        source="monster_scripts",
    )
    progress += 3

    for start, end in dialog_reclaim_ranges(world):
        world.sprites.animation_data_banks.append(AnimationBank(start, end))

    unused = world.action_scripts.get_unused_range()
    if unused:
        world.sprites.animation_data_banks.append(
            AnimationBank(unused[0], unused[1])
        )

    # Reserve 0x3AFA00-0x3B0000 for item descriptions by limiting battle animations
    world.battle_animations[0x3A].set_bank_end(0x3AFA00)
    unused_ranges = world.battle_animations[0x3A].get_unused_ranges()
    world.items.add_additional_desc_range(0x3AFA00, 0x3B0000)
    for start, end in unused_ranges:
        world.sprites.animation_data_banks.append(AnimationBank(start, end))

    for start, end in world.monster_scripts.get_unused_ranges():
        world.sprites.animation_data_banks.append(AnimationBank(start, end))

    # Sprite graphics patch (now has access to reclaimed animation banks)
    world._report_progress("Assembling graphics...", progress)

    # Sprites 490 (Smithy) and 491 (Smithy extended/"Shyper") must share
    # the same tile group so their subtile ordering matches - battle
    # animation events 82/86 use sprite 491's sequences interchangeably
    # with sprite 490's during the Smithy fight.
    banks = [(int(b.start), int(b.end)) for b in world.sprites.animation_data_banks]
    world.sprite_reclaim_banks = banks

    writes: list[tuple[int, bytes]] | None = None
    blob, world.pending_sprite_blob = world.pending_sprite_blob, None
    if blob is not None:
        try:
            writes = deserialize_sprites(blob, banks, world.version)
        except SpriteCacheError as exc:
            logger.warning("stored sprite render rejected (%s), repacking", exc)
    if writes is None:
        writes = [
            (addr, bytes(data))
            for addr, data in world.sprites.render(shared_image_groups=[[490, 491]])
        ]
    random.seed("post-sprites:%s" % world.seed)
    world.sprite_writes = writes
    for addr, data in writes:
        patch.add_data(addr, data, source="sprites")
    progress += 3

    # World map / file-select / overworld walker character overrides
    # are applied below in the non_mario_character block once we've
    # computed starter and i.

    if random.randint(0, 100) < 10:
        world.battle_dialogs.battle_messages[38] = "Wanna double you're coins?"

    # UncapMaxFP: Royal Syrup's vanilla _inflict=99 caps the heal at 99 FP
    # even though the item description reads "Recovers all Flower Pts." Bump
    # to 255 so the heal saturates at whatever max FP the player has.
    #
    # This is only safe alongside the RESTORE_FP rewrite in
    # asm/uncap_max_fp.py (item 6 in its docstring): vanilla $C2:C040 adds
    # the heal amount to current FP with an 8-bit ADC and ignores the carry,
    # so 255 wraps to cur - 1. Both changes are gated on UncapMaxFP; do not
    # ship one without the other. Must run before world.items.render() below.
    if world.settings.isflag_enabled(UncapMaxFP):
        world.get_item(RoyalSyrupItem).set_inflict(255)

    with ThreadPoolExecutor() as executor:
        futures = {
            "battle_dialogs": executor.submit(world.battle_dialogs.render),
            "enemies": executor.submit(world.enemies.render),
            "enemy_attacks": executor.submit(world.enemy_attacks.render),
            "items": executor.submit(world.items.render),
            "packets": executor.submit(world.packets.render),
            "battle_packs": executor.submit(world.battle_packs.render),
            "rooms": executor.submit(world.rooms.render),
            "shops": executor.submit(world.shops.render),
            "spells": executor.submit(world.spells.render),
            "allies": executor.submit(world.allies.render),
            "world_map_locations": executor.submit(world.world_map_locations.render),
        }
        for key in [
            "battle_dialogs",
            "enemies",
            "enemy_attacks",
            "items",
            "packets",
            "battle_packs",
            "rooms",
            "shops",
            "spells",
            "allies",
            "world_map_locations",
        ]:
            result = futures[key].result()
            patch.add_dict(result, source=key)
            progress += 2
            world._report_progress("Assembling object data...", progress)

    world._report_progress("Writing patch...", 95)
    credits_data = update_credits(world)
    patch.add_dict(credits_data, source="credits")

    # Always-on byte patches.
    patch.add_dict(asm.key_item_inventory.get_patch(), source="key_item_inventory")
    # Unconditional: Debug Candy is always protected, and the hooks are inert
    # for any item whose no_sell bit is clear.
    patch.add_dict(asm.unsellable_items.get_patch(), source="unsellable_items")
    patch.add_dict(asm.equip_menu_sort.get_patch(), source="equip_menu_sort")
    patch.add_dict(asm.special_items_menu_sort.get_patch(), source="special_items_menu_sort")
    # Coin counter cap 999 -> 9999 (overworld add-coins, battle reward,
    # X-menu). Reproduces the legacy open_mode.json clamp edits so the
    # JSON entries can be retired.
    patch.add_dict(asm.uncap_coins.get_patch(), source="uncap_coins")
    # Always-on overworld engine substrate for the non-Mario-protagonist
    # system: ally-loader char-0 collapse ($9009) + name-targeted resolver
    # gutting ($3EB2/$E42C). Relocates the open_mode.json patched bytes
    # verbatim (LOAD-BEARING - never restore vanilla). non_mario_character
    # layers the per-seed sprite base ($9B86) on top of this.
    patch.add_dict(asm.protagonist_static.get_patch(), source="protagonist_static")
    # Skip the opening garden intro on new game + load game (the two
    # LazyShell "Intro" editor checkboxes, both set in open_mode.json).
    patch.add_dict(asm.disable_garden_intro.get_patch(), source="disable_garden_intro")
    # Custom intro / title-screen GFX, streamed from the title_screen.bin
    # asset (render() does not regenerate the title screen).
    patch.add_dict(asm.title_screen.get_patch(), source="title_screen")
    patch.add_dict(asm.learn_special_event.get_patch(), source="learn_special_event")
    patch.add_dict(asm.dialogue_text_expansion.get_patch(), source="dialogue_text_expansion")
    patch.add_dict(asm.battle_attribute_patches.get_patch(), source="battle_attribute_patches")
    patch.add_dict(asm.menu_item_always_available.get_patch(), source="menu_item_always_available")
    patch.add_dict(asm.grid_menu_navigation.get_patch(), source="grid_menu_navigation")
    patch.add_dict(asm.title_loop.get_patch(), source="title_loop")
    # Bound the character id the game-over auto-continue ($C3:7B4C) turns
    # into an MVN offset. Unclamped it can walk into the saved event-flag
    # block, which reads as "EXP not kept + NPCs despawned" after a
    # ResetAndChooseGame. Vanilla bug; see the module docstring.
    patch.add_dict(asm.game_over_continue_fix.get_patch(), source="game_over_continue_fix")

    # Flag-gated byte patches.
    if (world.settings.is_flag_value(EXPChallenge, EXPChallengeOptions.NONE)
            or world.settings.is_flag_value(BossShuffleScaleStats, BossScaleOptions.GODMODE)
            or world.settings.debug_mode):
        patch.add_dict(asm.no_exp.get_patch(), source="no_exp")

    if world.settings.isflag_enabled(ShowEquips):
        patch.add_dict(asm.show_equips.get_patch(), source="show_equips")

    if world.settings.isflag_enabled(UncapMaxFP):
        patch.add_dict(asm.uncap_max_fp.get_patch(), source="uncap_max_fp")

    if world.selected_music_ids:
        patch.add_dict(
            asm.selected_music.get_patch(world.selected_music_ids),
            source="selected_music",
        )

    if world.settings.isflag_enabled(HoldB):
        patch.add_dict(asm.hold_b.get_patch(), source="hold_b")

    # Blanks the DUMMY effect's tile data so the NewEffectObject rewrites in
    # apply_cosmetic_settings have an effect id that renders nothing.
    if world.settings.isflag_enabled(RemoveFlashes):
        patch.add_dict(
            asm.blank_dummy_effect.get_patch(), source="blank_dummy_effect"
        )

    if world.settings.isflag_enabled(RandomMinecartTrack):
        patch.add_dict(
            get_minecart_track_patch(world), source="moleville_track"
        )

    if world.settings.isflag_enabled(JapaneseABXY):
        world.sprite_palettes.get_palette(
            SPAL293_ABXY_ACTION_BUTTON_SELECTION_IN_BATTLE
        ).set_colors(
            [
                0xFFFFFF,
                0x630000,
                0xB58C29,
                0xD6CE4A,
                0x42944A,
                0x187B21,
                0x394294,
                0x18188C,
                0x000042,
                0xFF4A52,
                0xDE3139,
                0x312908,
                0x083110,
                0x000000,
                0x000000,
            ]
        )
        world.sprite_palettes.get_palette(
            SPAL379_ABXY_BUTTONS_FROM_BOWYER_S_BUTTON_LOCK
        ).set_colors(
            [
                0xFFFFFF,
                0x630000,
                0x949494,
                0x4A4A4A,
                0x42944A,
                0x187B21,
                0x394294,
                0x18188C,
                0x000042,
                0xFF4A52,
                0xDE3139,
                0x8C3100,
                0x083110,
                0x000000,
                0x000000,
            ]
        )

    starter = cast(CharacterPrize, world.get_location(StartingCharacter1).prize).ally
    world.file_select_character = starter.name

    # World map sprite + file-select graphic + overworld walker hooks
    # + file-select name strings - all character-display patches in
    # one place.
    patch.add_dict(
        asm.non_mario_character.get_patch(
            starter_index=starter.index,
            overworld_index=world.overworld_character.ally.index,
            file_select_names=world.file_select_names,
        ),
        source="non_mario_character",
    )

    if world.settings.isflag_enabled(FixInvincibility):
        patch.add_dict(asm.invincibility_fix.get_patch(), source="invincibility_fix")

    if world.settings.debug_mode:
        patch.add_dict(asm.debug_fp.get_patch(), source="debug_fp")

    # Palettes
    patch.add_dict(world.sprite_palettes.render(), source="sprite_palettes")
    patch.add_dict(world.event_palettes.render(), source="event_palettes")
    for s in world.spells.spells:
        if isinstance(s, CharacterSpell):
            patch.add_dict(s.palette_patch, source="spell_palettes")

    patch.add_dict(asm.room_174_battlefield.get_patch(), source="room_174_battlefield")
    patch.add_dict(asm.room_325_solidity.get_patch(), source="room_325_solidity")
    patch.add_dict(asm.booster_hill_fixes.get_patch(), source="booster_hill_fixes")
    patch.add_dict(asm.star_piece_sprite_fix.get_patch(), source="star_piece_sprite_fix")
    patch.add_dict(asm.sprite_group_whitelist.get_patch(), source="sprite_group_whitelist")
    patch.add_dict(asm.battle_init.get_patch(), source="battle_init")
    patch.add_dict(asm.battle_intro_hdma_fix.get_patch(), source="battle_intro_hdma_fix")
    patch.add_dict(asm.exp_star_music_sticky.get_patch(), source="exp_star_music_sticky")

    # The "Victory Against Culex" fanfare is selected by a hardcoded
    # comparison against Culex's vanilla formation ID, which our renumbering
    # invalidates. Point it at whatever formations end up behind the Monstro
    # Town doors - the story boss and the postgame Culex 3D rematch.

    culex_music_formation_ids: list[int] = []
    for door_pack_id in (PACK216_MONSTRO_DOOR_BOSS, PACK055_MONSTRO_DOOR_POSTGAME):
        door_formations = {
            formation.formation_id
            for formation in world.battle_packs.packs[door_pack_id].formations
        }
        assert len(door_formations) == 1, (
            f"pack {door_pack_id} must hold a single formation for the victory "
            f"music selector, got {door_formations}"
        )
        door_formation_id = door_formations.pop()
        assert door_formation_id is not None
        culex_music_formation_ids.append(door_formation_id)
    patch.add_dict(
        asm.culex_victory_music.get_patch(culex_music_formation_ids),
        source="culex_victory_music",
    )

    # Packet allocation patch - allow low-VRAM packets (those with
    # goes_to_npc_slot_buffer = True) to use the NPC slot path
    # instead of the bitmap allocator.
    npc_slot_packet_ids: set[int] = {
        packet.packet_id
        for packet in world.packets.packets
        if isinstance(packet, Packet) and packet.goes_to_npc_slot_buffer
    }
    patch.add_dict(
        asm.packet_allocation.get_patch(npc_slot_packet_ids),
        source="packet_allocation",
    )

    patch.add_dict(asm.room_layouts.get_patch(), source="room_layouts")

    # Belome 3 spell-block + Enduring Brooch ASM hook (always-on).
    # The blocked-spell list inside the apply-damage helper changes
    # when InfuseSpellElements is on (those infused spells become
    # elemental, and Belome 3's rule is to nullify only
    # NON-elemental spells).
    patch.add_dict(
        asm.belome3_brooch.get_patch(
            infuse_spell_elements=world.settings.isflag_enabled(InfuseSpellElements)
        ),
        source="belome3_brooch",
    )

    # Battlefield underwater-palette whitelist (always-on). Without
    # this, BF14/BF34/BF38 force every actor onto a "+4 palette"
    # path (palette pointer +$78 = 4 × 30-byte monster palettes)
    # and any monster without a real underwater variant reads
    # garbage from a neighbor's palette. The hook gates the path
    # to the curated whitelist in
    # asm/battlefield_underwater_palette.py.
    patch.add_dict(
        asm.battlefield_underwater_palette.get_patch(),
        source="battlefield_underwater_palette",
    )

    # FxPakPro Archipelago NMI hook - DISABLED (proof of concept only).
    # Enabling NMI ($4200 bit 7) during gameplay causes the vanilla NMI handler
    # ($C0:0283) to fire every VBlank. That handler is NOT a no-op - it calls the
    # SA-1 message dispatcher ($0691) which corrupts battle state including
    # $7E0926 (party size). All FxPak/NMI patching is commented out.
    # patch.add_data(NMI_VECTOR_ROM_OFFSET, NMI_VECTOR_NEW)
    # patch.add_data(EMU_NMI_VECTOR_ROM_OFFSET, EMU_NMI_VECTOR_NEW)
    # patch.add_data(TRAMPOLINE_ROM_OFFSET, TRAMPOLINE_CODE)
    # patch.add_data(HOOK_ROM_OFFSET, NMI_HOOK_CODE)
    # for rom_offset, _old, new in NMITIMEN_PATCHES:
    #     patch.add_data(rom_offset, bytes([new]))

    # ROM title + version metadata (SNES header + name-entry screen).
    patch.add_dict(
        asm.rom_metadata.get_patch(seed=world.seed, version=world.version),
        source="rom_metadata",
    )

    world._cached_patch = patch

    return patch


__all__ = ['get_patch']
