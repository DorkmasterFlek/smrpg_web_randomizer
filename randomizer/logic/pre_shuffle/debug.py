"""Starting inventory setup for debug mode and Free Shops."""
from __future__ import annotations
from typing import TYPE_CHECKING

from randomizer.data.variables.variable_names import PRIMARY_TEMP_7000
from randomizer.debug import load_debug_config, get_item_class
from randomizer.data.variables.event_script_names import E3840_STARTER_DEBUG_ITEMS
from randomizer.types.flags import FreeShops
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands.commands import (
        AddToInventory, AddCoins, AddFrogCoins, Return, SetVarToConst
    )

if TYPE_CHECKING:
    from ...types.gameworld import GameWorld

FREE_SHOPS_COINS = 9999
FREE_SHOPS_FROG_COINS = 999


def apply_starting_items_and_coins(world: GameWorld) -> None:
    """Fill E3840, which runs once at new game, with starting coins and items."""

    coins = 0
    frog_coins = 0
    items = []

    if world.settings.debug_mode:
        config = load_debug_config()
        coins = config.get("starting_coins", FREE_SHOPS_COINS)
        frog_coins = config.get("starting_frog_coins", 99)
        for item_name in config.get("items", {}).get("start", []):
            item_cls = get_item_class(item_name)
            if item_cls is not None:
                items.append(item_cls)

    if world.settings.isflag_enabled(FreeShops):
        coins = max(coins, FREE_SHOPS_COINS)
        frog_coins = max(frog_coins, FREE_SHOPS_FROG_COINS)

    if not coins and not frog_coins and not items:
        return

    commands = []

    if coins > 0:
        commands.append(SetVarToConst(PRIMARY_TEMP_7000, coins))
        commands.append(AddCoins(PRIMARY_TEMP_7000))

    if frog_coins > 0:
        commands.append(SetVarToConst(PRIMARY_TEMP_7000, frog_coins))
        commands.append(AddFrogCoins(PRIMARY_TEMP_7000))

    for item_cls in items:
        commands.append(AddToInventory(item_cls))

    commands.append(Return())

    script = world.event_scripts.get_script_by_id(E3840_STARTER_DEBUG_ITEMS)
    assert script is not None, "Event script E3840_STARTER_DEBUG_ITEMS not found"
    script.set_contents(commands)
