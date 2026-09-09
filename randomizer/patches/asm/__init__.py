"""Raw ASM / byte-level ROM patches.

Each module in this package exposes a get_patch(...) -> dict[int, bytes]
function returning a mapping of ROM offset to bytes that the caller passes
to Patch.add_dict. Gameworld decides whether to call each module based
on flags / settings; the modules themselves are concerned only with
generating bytes.

Modules
-------

ASM hooks (multi-site / runtime-built):
    * :mod:battle_intro_hdma_fix - Order-gate the sprite-palette HDMA
      enable so it cannot bleed during the battle intro (the neon-block
      glitch).
    * :mod:battlefield_underwater_palette - Whitelist gate for the
      "+4 palette" path in BF14/BF34/BF38 so non-underwater monsters
      keep their normal colors.
    * :mod:belome3_brooch - Belome 3 spell-block + Enduring Brooch.
    * :mod:exp_star_music_sticky - Keep the EXP-star (Invincible Star)
      music overriding room BGM across room transitions when it is
      started via PlayMusicAtCurrentVolume.
    * :mod:invincibility_fix - Red Essence dispel guard.
    * :mod:packet_allocation - Packet allowlist routine for NPC slots.

Always-on byte patches:
    * :mod:key_item_inventory - Expand key-item inventory size.
    * :mod:uncap_coins - Raise the current-coins cap from 999 to 9999
      (overworld add-coins, battle reward, X-menu).
    * :mod:protagonist_static - Always-on overworld engine substrate
      (ally-loader char-0 collapse + name-targeted resolver gutting) for
      the non-Mario-protagonist system.
    * :mod:disable_garden_intro - Skip the opening garden intro on both
      new game and load game.
    * :mod:title_screen - Custom intro / title-screen GFX, streamed from
      the title_screen.bin asset (render() does not regenerate it).
    * :mod:static_data - Render-disjoint open-mode base data (effect
      animations/palettes, tilesets, gap data) from static_data.bin;
      applied before the palette cosmetics.
    * :mod:learn_special_event - Custom "learn special ability" event command.
    * :mod:dialogue_text_expansion - Dialogue codes 0x18/0x19 -> bank $E4 text.
    * :mod:dialog_font_item_punctuation - Give the dialogue font the !
      # - ' glyphs item names encode at codes 0x7B-0x7E, so an item
      name drawn with that font (battle spoils box, [0x70A7] substitution)
      reads the same as it does in the menu.
    * :mod:battle_attribute_patches - Confuse-status mask + attribute table.
    * :mod:menu_item_always_available - Force a $40:30E3 menu item available.
    * :mod:grid_menu_navigation - 2-D grid-menu cursor rework.
    * :mod:equip_menu_sort - Sort the equipment list when the Equip menu opens.
    * :mod:special_items_menu_sort - Sort the key-items list when its menu opens.
    * :mod:title_loop - Title screen loops forever (no attract-mode demo).
    * :mod:game_over_continue_fix - Clamp the character id the game-over
      auto-continue turns into an MVN offset, so a bad multiply or slot
      count cannot scribble over the saved event flags (lost EXP +
      despawned NPCs after ResetAndChooseGame).
    * :mod:battle_init - Copy overworld party size to battle party size.
    * :mod:star_piece_sprite_fix - Credits ending sequence sprite ID.
    * :mod:room_layouts - Room area-layout records.
    * :mod:room_174_battlefield - Force Sea Enclave for room 174 fights.
    * :mod:room_325_solidity - Mushroom Kingdom doorway chest fix.
    * :mod:sprite_group_whitelist - Relocated engine sprite-group
      whitelist; restores the Green Yoshi entry alongside the
      alternate-protagonist entry (room 34 Yoshi-riding).
    * :mod:rom_metadata - ROM title + version text.

Flag-gated byte patches:
    * :mod:no_exp - Zero EXP table.
    * :mod:star_exp_progression - Balanced EXP-per-hit curve for the
      "Star Pieces" / "Bosses" EXP star challenge; mutually exclusive
      with no_exp.
    * :mod:show_equips - Show equipped item bitmasks in menu.
    * :mod:uncap_max_fp - Uncap max FP from 99 to 255.
    * :mod:unsellable_items - Bar no_sell items from being sold or discarded.
    * :mod:selected_music - Battle music ID overrides.
    * :mod:culex_victory_music - Point the "Victory Against Culex" fanfare at
      whatever formation ends up behind the Monstro Town door, instead of
      Culex's stale vanilla formation ID.
    * :mod:hold_b - Hold-B-to-advance dialog patch.
    * :mod:debug_fp - Starting FP override under debug mode.
    * :mod:non_mario_character - Starter / overworld / file-select
      sprite redirects when the player is not Mario.
    * :mod:blank_dummy_effect - Erase the tile data behind the shared DUMMY
      battle effect so RemoveFlashes has an effect id that draws nothing.
"""

from . import (
    battle_init,
    battle_intro_hdma_fix,
    blank_dummy_effect,
    battlefield_underwater_palette,
    belome3_brooch,
    booster_hill_fixes,
    culex_victory_music,
    debug_fp,
    dialog_font_item_punctuation,
    disable_garden_intro,
    exp_star_music_sticky,
    game_over_continue_fix,
    hold_b,
    invincibility_fix,
    key_item_inventory,
    no_exp,
    battle_attribute_patches,
    dialogue_text_expansion,
    equip_menu_sort,
    grid_menu_navigation,
    learn_special_event,
    menu_item_always_available,
    non_mario_character,
    packet_allocation,
    protagonist_static,
    rom_metadata,
    room_174_battlefield,
    room_325_solidity,
    room_layouts,
    selected_music,
    show_equips,
    special_items_menu_sort,
    sprite_group_whitelist,
    star_exp_progression,
    star_piece_sprite_fix,
    static_data,
    title_loop,
    title_screen,
    uncap_coins,
    uncap_max_fp,
    unsellable_items,
)

__all__ = [
    "battle_init",
    "battle_intro_hdma_fix",
    "battlefield_underwater_palette",
    "belome3_brooch",
    "booster_hill_fixes",
    "culex_victory_music",
    "blank_dummy_effect",
    "debug_fp",
    "dialog_font_item_punctuation",
    "disable_garden_intro",
    "exp_star_music_sticky",
    "game_over_continue_fix",
    "hold_b",
    "invincibility_fix",
    "key_item_inventory",
    "no_exp",
    "battle_attribute_patches",
    "dialogue_text_expansion",
    "equip_menu_sort",
    "grid_menu_navigation",
    "learn_special_event",
    "menu_item_always_available",
    "non_mario_character",
    "packet_allocation",
    "title_loop",
    "protagonist_static",
    "rom_metadata",
    "room_174_battlefield",
    "room_325_solidity",
    "room_layouts",
    "selected_music",
    "show_equips",
    "special_items_menu_sort",
    "sprite_group_whitelist",
    "star_exp_progression",
    "star_piece_sprite_fix",
    "static_data",
    "title_screen",
    "uncap_coins",
    "uncap_max_fp",
    "unsellable_items",
]
