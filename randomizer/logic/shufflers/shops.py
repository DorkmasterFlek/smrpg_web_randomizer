"""Shop shuffling logic."""

from __future__ import annotations
from ...types.prize import ItemPrize
import random
from typing import TYPE_CHECKING, Callable, cast

from ...data.variables.dialog_names import *
from ...types.item import Item, Equipment
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import SetVarToConst
from ...data.items.items import SeeYaItem
from ...data.shops.shops import SH03_FROG_DISCIPLE, shop_collection
from smrpgpatchbuilder.datatypes.items.classes import Weapon, Armor, Accessory
from ...data.items.items import (
        GoodieBagItem,
        PickMeUpItem,
        MushroomItem,
        MidMushroomItem,
        MaxMushroomItem,
        HoneySyrupItem,
        MapleSyrupItem,
        AbleJuiceItem,
        BracerItem,
        EnergizerItem,
        YoshiCookieItem,
        PureWaterItem,
        YoshiCandyItem,
        FroggieDrinkItem,
        MukuCookieItem,
        ElixirItem,
        FreshenUpItem,
        MushroomItem2,
        YoshiAdeItem,
        RedEssenceItem,
        KerokeroColaItem,
        MegalixirItem,
        RockCandyItem,
        CrystallineItem,
        PowerBlastItem,
        RoyalSyrupItem,
        IceBombItem,
        FireBombItem,
        SleepyBombItem,
        FrightBombItem,
        BadMushroomItem,
        SeeYaItem,
        EarlierTimesItem,
        ExpBoosterItem,
        CoinTrickItem,
        ScroogeRingItem,
        FireworksItem,
        ShinyStoneItem,
        CarboCookieItem,
        StarEggItem,
        LuckyJewelItem,
        MysteryEggItem,
        LambsLureItem,
        SheepAttackItem,
        FlowerBoxItem,
        FlowerJarItem,
    )
from ...types.flags import (
        ShopQuality,
        ShopQualities,
        BiasShopShuffle,
        PickMeUpAvailability,
        PickMeUpOptions,
        FreeShops,
        SeaGate,
        SeaGating,
        MonstroTownGate,
        MonstroTownGating,
        BarrelVolcanoGate,
        BarrelVolcanoGating,
        NimbusGate,
        NimbusGating,
        BowsersKeepGate,
        BowsersKeepGating,
        FireworksSetting,
        FireworksOptions,
        NoStarEgg,
    )
from ...data.shops.shops import (
        SH03_FROG_DISCIPLE,
        SH06_FROG_COIN_EMPORIUM,
        SH07_SEA_AND_SHIP_SHAMAN,
        SH08_SEASIDE_TOWN_MINION,
        SH09_JUICE_BAR_BASE,
        SH10_JUICE_BAR_ALTO,
        SH11_JUICE_BAR_TENOR,
        SH12_JUICE_BAR_SOPRANO,
        SH13_SEASIDE_WEAPON,
        SH14_SEASIDE_ARMOR,
        SH15_SEASIDE_ACCESSORY,
        SH16_SEASIDE_HEALTH_FOOD,
        SH17_MONSTRO,
        SH18_VOLCANO_ITEM,
        SH19_VOLCANO_ARMOR,
        SH20_GOOMBETTE,
        SH21_NIMBUS_LAND,
        SH22_KEEP_1,
        SH23_KEEP_2,
        SH24_FACTORY_TOAD,
    )
from randomizer.logic.progression.prizelocations import (
        FrogDiscipleLocation1,
        FrogDiscipleLocation2,
        FrogDiscipleLocation3,
        FrogDiscipleLocation4,
        FrogDiscipleLocation5,
        StartingItem1Location,
        StartingItem2Location,
        StartingItem3Location,
        StartingItem4Location,
    )
from randomizer.logic.progression.prizelocations.access import (
        can_access_factory,
        can_access_juice_bar_alto,
        can_access_juice_bar_soprano,
        can_access_juice_bar_tenor,
        can_access_keep,
        can_access_monstro_town,
        can_access_outer_nimbus,
        can_access_sea,
        can_access_volcano,
    )
from randomizer.types.logic import (Inventory)
from .equipment import (
        calc_equip_price,
        frog_coins_per_coin,
    )

if TYPE_CHECKING:
    from ...types.gameworld import GameWorld
    from smrpgpatchbuilder.datatypes.items.classes import Item as BaseItem

SHOP_ACCESS: dict[int, Callable[["GameWorld", Inventory], bool]] = {
    SH03_FROG_DISCIPLE: can_access_sea,
    SH07_SEA_AND_SHIP_SHAMAN: can_access_sea,
    SH08_SEASIDE_TOWN_MINION: can_access_sea,
    SH10_JUICE_BAR_ALTO: can_access_juice_bar_alto,
    SH11_JUICE_BAR_TENOR: can_access_juice_bar_tenor,
    SH12_JUICE_BAR_SOPRANO: can_access_juice_bar_soprano,
    SH13_SEASIDE_WEAPON: can_access_sea,
    SH14_SEASIDE_ARMOR: can_access_sea,
    SH15_SEASIDE_ACCESSORY: can_access_sea,
    SH16_SEASIDE_HEALTH_FOOD: can_access_sea,
    SH17_MONSTRO: can_access_monstro_town,
    SH18_VOLCANO_ITEM: can_access_volcano,
    SH19_VOLCANO_ARMOR: can_access_volcano,
    SH20_GOOMBETTE: can_access_monstro_town,
    SH21_NIMBUS_LAND: can_access_outer_nimbus,
    SH22_KEEP_1: can_access_keep,
    SH23_KEEP_2: can_access_keep,
    SH24_FACTORY_TOAD: can_access_factory,
}

STARTING_ITEM_LOCATIONS = (
    StartingItem1Location,
    StartingItem2Location,
    StartingItem3Location,
    StartingItem4Location,
)


def starting_inventory(world: GameWorld) -> Inventory:
    """Prizes the player holds before gaining control, from the starting item slots."""

    prizes = []
    for loc_type in STARTING_ITEM_LOCATIONS:
        location = world.locations.get(loc_type)
        if location is not None and location.prize is not None:
            prizes.append(location.prize)
    return Inventory(prizes)


def is_earlygame(shop_index: int, world: GameWorld, inventory: Inventory | None = None) -> bool:
    """Whether a shop can be reached at the start of the game."""

    gate = SHOP_ACCESS.get(shop_index)
    if gate is None:
        return True
    if inventory is None:
        inventory = starting_inventory(world)
    return gate(world, inventory)


VANILLA_SHOP_ITEMS: frozenset[type[BaseItem]] = frozenset(
    item
    for shop in shop_collection.shops
    if shop is not None
    for item in (shop.items or [])
    if item is not None
)


def reprice_nonvanilla_shop_items(world: GameWorld) -> None:
    """Reprice items that weren't shop items in the original game."""

    if world.settings.isflag_enabled(FreeShops):
        return

    for shop in world.shops.shops:
        if shop is None:
            continue
        frog_coin_shop = shop.buy_frog_coin_one or shop.buy_frog_coin
        for item_type in (shop.items or []):
            if item_type is None or item_type in VANILLA_SHOP_ITEMS:
                continue
            item = world.items.get_by_type(item_type)
            if not isinstance(item, Equipment):
                continue
            item.set_price(calc_equip_price(item, frog_coin_shop))


def exclude_seeya_from_frog_disciple(world: GameWorld) -> None:
    """Remove SeeYaItem from the Frog Disciple shop when SeeYa flag is enabled and shops aren't shuffled."""

    shop = world.shops.shops[SH03_FROG_DISCIPLE]
    current_items = [item for item in (shop.items or []) if item is not None and item != SeeYaItem]
    shop.set_items(current_items)


def shuffle_shops(world: GameWorld) -> None:
    """Shuffle the contents of all shops based on settings."""

    quality = world.settings.get_flag(ShopQuality).selected
    bias_enabled = world.settings.isflag_enabled(BiasShopShuffle)
    pickmeups = world.settings.get_flag(PickMeUpAvailability).selected
    no_pickmeups = pickmeups == PickMeUpOptions.NONE
    free_shops = world.settings.isflag_enabled(FreeShops)

    FROG_DISCIPLE_SHOP = SH03_FROG_DISCIPLE
    FROG_COIN_EMPORIUM = SH06_FROG_COIN_EMPORIUM
    JUICE_BAR_BASE = SH09_JUICE_BAR_BASE
    JUICE_BAR_ALTO = SH10_JUICE_BAR_ALTO
    JUICE_BAR_TENOR = SH11_JUICE_BAR_TENOR
    JUICE_BAR_SOPRANO = SH12_JUICE_BAR_SOPRANO
    DUMMY_SHOPS = frozenset(range(25, 33))
    JUICE_BAR_SHOPS = frozenset(
        {JUICE_BAR_BASE, JUICE_BAR_ALTO, JUICE_BAR_TENOR, JUICE_BAR_SOPRANO}
    )

    ORIGINAL_FROG_COIN_ITEMS: set[type[BaseItem]] = {
        SeeYaItem,
        EarlierTimesItem,
        ExpBoosterItem,
        CoinTrickItem,
        ScroogeRingItem,
        SleepyBombItem,
        BracerItem,
        EnergizerItem,
        CrystallineItem,
        PowerBlastItem,
    }

    frog_disciple_items: list[type[BaseItem] | None] = []
    frog_disciple_locations = [
        FrogDiscipleLocation1,
        FrogDiscipleLocation2,
        FrogDiscipleLocation3,
        FrogDiscipleLocation4,
        FrogDiscipleLocation5,
    ]
    for loc_type in frog_disciple_locations:
        loc = world.locations.get(loc_type)
        if loc and loc.prize:
            if isinstance(loc.prize, ItemPrize):
                prize_item = loc.prize.item
                if prize_item:
                    frog_disciple_items.append(prize_item)

    world.shops.shops[FROG_DISCIPLE_SHOP].set_items(frog_disciple_items)

    should_get_better_items = [
        SH06_FROG_COIN_EMPORIUM,
        SH08_SEASIDE_TOWN_MINION,
        SH11_JUICE_BAR_TENOR,
        SH12_JUICE_BAR_SOPRANO,
        SH13_SEASIDE_WEAPON,
        SH14_SEASIDE_ARMOR,
        SH15_SEASIDE_ACCESSORY,
        SH16_SEASIDE_HEALTH_FOOD,
        SH23_KEEP_2,
        SH24_FACTORY_TOAD,
    ]
    if not world.settings.is_flag_value(SeaGate, SeaGating.OPEN):
        should_get_better_items.append(SH07_SEA_AND_SHIP_SHAMAN)
    if not world.settings.is_flag_value(MonstroTownGate, MonstroTownGating.OPEN):
        should_get_better_items.extend([SH17_MONSTRO, SH20_GOOMBETTE])
    if not world.settings.is_flag_value(BarrelVolcanoGate, BarrelVolcanoGating.OPEN):
        should_get_better_items.extend([SH18_VOLCANO_ITEM, SH19_VOLCANO_ARMOR])
    if world.settings.is_flag_value(NimbusGate, NimbusGating.MEGASMILAX):
        should_get_better_items.append(SH21_NIMBUS_LAND)
    if not world.settings.is_flag_value(BowsersKeepGate, BowsersKeepGating.OPEN):
        should_get_better_items.extend([SH22_KEEP_1])

    start_inventory = starting_inventory(world)
    early_shops = frozenset(
        shop.index
        for shop in world.shops.shops
        if shop is not None
        and shop.index not in DUMMY_SHOPS
        and not (shop.buy_frog_coin or shop.buy_frog_coin_one)
        and is_earlygame(shop.index, world, start_inventory)
    )

    low_impact_items = world.low_impact_items
    high_impact_items = world.high_impact_items
    highest_impact_items = world.highest_impact_items
    low_impact_equip = world.low_impact_equip
    high_impact_equip = world.high_impact_equip
    highest_impact_equip = world.highest_impact_equip

    original_shop_data: dict[int, dict] = {}
    original_item_shop_count: dict[type[BaseItem], int] = {}
    for shop in world.shops.shops:
        if shop is None:
            continue
        orig_items = [i for i in shop.items if i is not None]
        original_shop_data[shop.index] = {
            "has_weapon": any(issubclass(i, Weapon) for i in orig_items),
            "has_armor": any(issubclass(i, Armor) for i in orig_items),
            "has_accessory": any(issubclass(i, Accessory) for i in orig_items),
            "has_consumable": any(
                not issubclass(i, (Weapon, Armor, Accessory)) for i in orig_items
            ),
            "original_items": orig_items,
            "original_count": len(orig_items),
        }
        if shop.index != FROG_DISCIPLE_SHOP:
            for item in orig_items:
                original_item_shop_count[item] = (
                    original_item_shop_count.get(item, 0) + 1
                )

    current_item_shop_count: dict[type[BaseItem], int] = {}

    if quality == ShopQualities.EMPTY:
        for shop in world.shops.shops:
            if shop is None:
                continue
            shop.set_items([GoodieBagItem])
        return

    def get_item_pool(
        quality: ShopQualities, is_equipment: bool = False
    ) -> tuple[list, list, list]:
        """Returns (low, high, highest) pools based on quality."""
        if is_equipment:
            if quality == ShopQualities.ORIGINAL:
                orig_equip_in_shops: set = set()
                for shop in world.shops.shops:
                    if shop is None or shop.index == FROG_DISCIPLE_SHOP:
                        continue
                    for item in shop.items:
                        if item and issubclass(item, (Weapon, Armor, Accessory)):
                            orig_equip_in_shops.add(item)
                return (
                    [e for e in low_impact_equip if e in orig_equip_in_shops],
                    [e for e in high_impact_equip if e in orig_equip_in_shops],
                    [e for e in highest_impact_equip if e in orig_equip_in_shops],
                )
            elif quality == ShopQualities.MOSTLY_RANDOM:
                return (low_impact_equip, high_impact_equip, [])
            else:
                return (low_impact_equip, high_impact_equip, highest_impact_equip)
        else:
            if quality == ShopQualities.ORIGINAL:
                orig_in_shops: set = set()
                for shop in world.shops.shops:
                    if shop is None or shop.index == FROG_DISCIPLE_SHOP:
                        continue
                    for item in shop.items:
                        if item and not issubclass(item, (Weapon, Armor, Accessory)):
                            orig_in_shops.add(item)
                return (
                    [i for i in low_impact_items if i in orig_in_shops],
                    [i for i in high_impact_items if i in orig_in_shops],
                    [i for i in highest_impact_items if i in orig_in_shops],
                )
            elif quality == ShopQualities.MOSTLY_RANDOM:
                return (low_impact_items, high_impact_items, [])
            else:
                return (low_impact_items, high_impact_items, highest_impact_items)

    low_consumables, high_consumables, highest_consumables = get_item_pool(
        quality, is_equipment=False
    )
    low_equip, high_equip, highest_equip = get_item_pool(quality, is_equipment=True)

    if no_pickmeups:
        low_consumables = [i for i in low_consumables if i != PickMeUpItem]
        high_consumables = [i for i in high_consumables if i != PickMeUpItem]
        highest_consumables = [i for i in highest_consumables if i != PickMeUpItem]

    frog_emporium_items: set = set()
    frog_disciple_set = set(frog_disciple_items)

    def can_place_item(
        item_type: type[BaseItem] | None, shop_idx: int, current_items: list
    ) -> bool:
        """Check if an item can be placed in a shop."""
        if item_type is None:
            return False
        if item_type in current_items:
            return False
        if item_type in frog_emporium_items and shop_idx != FROG_COIN_EMPORIUM:
            return False
        if item_type is PickMeUpItem and shop_idx == FROG_COIN_EMPORIUM:
            return False
        if item_type in frog_disciple_set and shop_idx not in [
            FROG_DISCIPLE_SHOP,
            FROG_COIN_EMPORIUM,
        ]:
            return False
        if quality == ShopQualities.ORIGINAL:
            max_shops = original_item_shop_count.get(item_type, 0)
            current_shops = current_item_shop_count.get(item_type, 0)
            if current_shops >= max_shops:
                return False
        if shop_idx == FROG_COIN_EMPORIUM and quality in (
            ShopQualities.COMPLETELY_RANDOM, ShopQualities.ALL
        ):
            return True
        shop_data = original_shop_data.get(shop_idx, {})
        if issubclass(item_type, Weapon) and not shop_data.get("has_weapon", False):
            return False
        if issubclass(item_type, Armor) and not shop_data.get("has_armor", False):
            return False
        if issubclass(item_type, Accessory) and not shop_data.get(
            "has_accessory", False
        ):
            return False
        if not issubclass(item_type, (Weapon, Armor, Accessory)) and not shop_data.get(
            "has_consumable", False
        ):
            return False
        return True

    def select_item(
        shop_idx: int, current_items: list, prefer_high: bool = False
    ) -> type[BaseItem] | None:
        """Select an item for a shop based on bias and availability."""
        is_better_shop = shop_idx in should_get_better_items

        candidates = []
        weights = []

        all_low = low_consumables + low_equip
        all_high = high_consumables + high_equip
        all_highest = highest_consumables + highest_equip

        if bias_enabled:
            if is_better_shop:
                for item in all_highest:
                    if can_place_item(item, shop_idx, current_items):
                        candidates.append(item)
                        weights.append(5)
                for item in all_high:
                    if can_place_item(item, shop_idx, current_items):
                        candidates.append(item)
                        weights.append(3)
                for item in all_low:
                    if can_place_item(item, shop_idx, current_items):
                        candidates.append(item)
                        weights.append(1)
            else:
                for item in all_low:
                    if can_place_item(item, shop_idx, current_items):
                        candidates.append(item)
                        weights.append(5)
                for item in all_high:
                    if can_place_item(item, shop_idx, current_items):
                        candidates.append(item)
                        weights.append(1)
                for item in all_highest:
                    if can_place_item(item, shop_idx, current_items):
                        candidates.append(item)
                        weights.append(0.2)
        else:
            for item in all_low + all_high + all_highest:
                if can_place_item(item, shop_idx, current_items):
                    candidates.append(item)
                    weights.append(1)

        if not candidates:
            return None

        return random.choices(candidates, weights=weights, k=1)[0]

    shops_to_process = [
        s for s in world.shops.shops if s is not None and s.index != FROG_DISCIPLE_SHOP
    ]

    frog_emporium_shop = world.shops.shops[FROG_COIN_EMPORIUM]
    if frog_emporium_shop:
        shop_data = original_shop_data.get(FROG_COIN_EMPORIUM, {})
        target_count = min(15, max(1, shop_data.get("original_count", 5)))
        emporium_new_items: list[type[BaseItem] | None] = []

        for _ in range(target_count):
            item = select_item(FROG_COIN_EMPORIUM, emporium_new_items, prefer_high=True)
            if item:
                emporium_new_items.append(item)
                frog_emporium_items.add(item)
                current_item_shop_count[item] = current_item_shop_count.get(item, 0) + 1

        frog_emporium_shop.set_items(emporium_new_items)

    juice_bars = [
        JUICE_BAR_BASE,
        JUICE_BAR_ALTO,
        JUICE_BAR_TENOR,
        JUICE_BAR_SOPRANO,
    ]
    juice_bar_max_items = {
        JUICE_BAR_BASE: 12,
        JUICE_BAR_ALTO: 13,
        JUICE_BAR_TENOR: 14,
        JUICE_BAR_SOPRANO: 15,
    }
    juice_bar_items: dict[int, list[type[BaseItem] | None]] = {
        bar: [] for bar in juice_bars
    }

    def add_to_juice_bar_cascade(item: type[BaseItem], starting_tier: int) -> bool:
        """Add item to starting_tier and all higher tiers (if they have room). Returns True if item was added to at least the starting tier."""
        if quality == ShopQualities.ORIGINAL:
            shops_to_add = 0
            for i in range(starting_tier, len(juice_bars)):
                bar_idx = juice_bars[i]
                max_items = juice_bar_max_items[bar_idx]
                items_list = juice_bar_items[bar_idx]
                if len(items_list) < max_items and item not in items_list:
                    shops_to_add += 1

            max_shops = original_item_shop_count.get(item, 0)
            current_shops = current_item_shop_count.get(item, 0)
            if current_shops + shops_to_add > max_shops:
                return False

        added_to_start = False
        shops_added = 0
        for i in range(starting_tier, len(juice_bars)):
            bar_idx = juice_bars[i]
            max_items = juice_bar_max_items[bar_idx]
            items_list = juice_bar_items[bar_idx]
            if len(items_list) < max_items and item not in items_list:
                items_list.append(item)
                shops_added += 1
                if i == starting_tier:
                    added_to_start = True

        if shops_added > 0:
            current_item_shop_count[item] = (
                current_item_shop_count.get(item, 0) + shops_added
            )

        return added_to_start

    for tier_idx, bar_idx in enumerate(juice_bars):
        shop = world.shops.shops[bar_idx]
        if shop is None:
            continue

        max_items = juice_bar_max_items[bar_idx]
        current_items = juice_bar_items[bar_idx]

        attempts = 0
        while len(current_items) < max_items and attempts < 100:
            item = select_item(bar_idx, current_items)
            if item and item not in current_items:
                add_to_juice_bar_cascade(item, tier_idx)
            attempts += 1

    for bar_idx in juice_bars:
        shop = world.shops.shops[bar_idx]
        if shop is not None:
            shop.set_items(juice_bar_items[bar_idx])

    processed = {FROG_DISCIPLE_SHOP, FROG_COIN_EMPORIUM} | set(juice_bars)
    remaining_shops = [
        s for s in shops_to_process
        if s.index not in processed and s.index not in DUMMY_SHOPS
    ]

    if quality == ShopQualities.ALL:
        all_excluded: set[type[BaseItem]] = set()
        if not world.settings.is_flag_value(FireworksSetting, FireworksOptions.VANILLA):
            all_excluded.update([FireworksItem, ShinyStoneItem, CarboCookieItem])
        if world.settings.isflag_enabled(NoStarEgg):
            all_excluded.add(StarEggItem)

        all_pool_items = set(
            low_consumables + high_consumables + highest_consumables
            + low_equip + high_equip + highest_equip
        )

        ALL_MODE_SPECIAL_ITEMS = [
            StarEggItem, SeeYaItem, EarlierTimesItem, GoodieBagItem,
            LuckyJewelItem, MysteryEggItem, LambsLureItem, SheepAttackItem,
            FlowerBoxItem, FlowerJarItem,
        ]
        all_pool_items.update(ALL_MODE_SPECIAL_ITEMS)

        items_already_placed: set[type[BaseItem]] = set()
        for shop in world.shops.shops:
            if shop is None or shop.index == FROG_DISCIPLE_SHOP or shop.index in DUMMY_SHOPS:
                continue
            if shop.index in processed:
                for item in (shop.items or []):
                    if item is not None:
                        items_already_placed.add(item)

        guarantee_items = []
        for item_type in sorted(all_pool_items, key=lambda cls: cls.__name__):
            if item_type in items_already_placed:
                continue
            if item_type in all_excluded:
                continue
            if item_type in frog_emporium_items:
                continue
            if item_type in frog_disciple_set:
                continue
            item_inst = world.items.get_by_type(item_type)
            if item_inst and item_inst.price == 0:
                continue
            if item_inst and item_inst.no_sell:
                continue
            guarantee_items.append(item_type)

        random.shuffle(guarantee_items)

        shop_contents: dict[int, list[type[BaseItem]]] = {
            s.index: [] for s in remaining_shops
        }

        for item_type in guarantee_items:
            eligible = []
            for shop in remaining_shops:
                items = shop_contents[shop.index]
                if item_type in items:
                    continue
                if len(items) >= 15:
                    continue
                if not can_place_item(item_type, shop.index, items):
                    continue
                eligible.append((shop, len(items)))

            if eligible:
                eligible.sort(key=lambda x: x[1])
                min_count = eligible[0][1]
                emptiest = [s for s, c in eligible if c == min_count]
                target = random.choice(emptiest)
                shop_contents[target.index].append(item_type)
                current_item_shop_count[item_type] = current_item_shop_count.get(item_type, 0) + 1

        for shop in remaining_shops:
            shop_data_entry = original_shop_data.get(shop.index, {})
            target_count = min(15, max(1, shop_data_entry.get("original_count", 5)))
            current_items = shop_contents[shop.index]

            target_count = max(target_count, len(current_items))

            attempts = 0
            while len(current_items) < target_count and attempts < 100:
                item = select_item(shop.index, current_items)
                if item:
                    current_items.append(item)
                    current_item_shop_count[item] = current_item_shop_count.get(item, 0) + 1
                attempts += 1

            shop.set_items(current_items)

    else:

        for shop in remaining_shops:
            item = select_item(shop.index, [])
            if item:
                shop.set_items([item])
                current_item_shop_count[item] = current_item_shop_count.get(item, 0) + 1
            else:
                shop.set_items([])

        for shop in remaining_shops:
            shop_data_entry = original_shop_data.get(shop.index, {})
            target_count = min(15, max(1, shop_data_entry.get("original_count", 5)))
            current_items: list[type[BaseItem] | None] = [
                i for i in (shop.items or []) if i is not None
            ]

            for _ in range(target_count - len(current_items)):
                item = select_item(shop.index, current_items)
                if item:
                    current_items.append(item)
                    current_item_shop_count[item] = current_item_shop_count.get(item, 0) + 1

            shop.set_items(current_items)

    for shop in world.shops.shops:
        if shop is None or shop.index == FROG_DISCIPLE_SHOP or shop.index in DUMMY_SHOPS:
            continue
        current_items = [i for i in (shop.items or []) if i is not None]
        if len(current_items) == 0:
            raise RuntimeError(
                f"Shop index {shop.index} ended up with zero items after shuffling"
            )

    if pickmeups == PickMeUpOptions.EARLY:
        early_has_pickmeup = any(
            shop is not None
            and shop.index in early_shops
            and PickMeUpItem in (shop.items or [])
            for shop in world.shops.shops
        )

        if not early_has_pickmeup:
            candidates = [
                shop
                for shop in world.shops.shops
                if shop is not None
                and shop.index in early_shops
                and shop.index not in JUICE_BAR_SHOPS
                and PickMeUpItem not in (shop.items or [])
            ]
            with_room = [s for s in candidates if len(s.items or []) < 15]
            sold_consumables = [
                s
                for s in with_room
                if original_shop_data.get(s.index, {}).get("has_consumable", False)
            ]

            donors = [
                shop
                for shop in world.shops.shops
                if shop is not None
                and shop.index not in early_shops
                and shop.index != FROG_DISCIPLE_SHOP
                and shop.index not in DUMMY_SHOPS
                and shop.index not in JUICE_BAR_SHOPS
                and PickMeUpItem in (shop.items or [])
                and len([i for i in (shop.items or []) if i is not None]) > 1
            ]

            may_add = True
            if not donors and quality == ShopQualities.ORIGINAL:
                original_pickmeup_shops = original_item_shop_count.get(PickMeUpItem, 0)
                current_pickmeup_shops = current_item_shop_count.get(PickMeUpItem, 0)
                may_add = (
                    original_pickmeup_shops > 0
                    and current_pickmeup_shops < original_pickmeup_shops
                )

            target = None
            if sold_consumables:
                target = random.choice(sold_consumables)
            elif with_room:
                target = random.choice(with_room)
            elif candidates:
                target = random.choice(candidates)

            if target is not None and (donors or may_add):
                if donors:
                    donor = random.choice(donors)
                    donor.set_items(
                        [i for i in (donor.items or []) if i != PickMeUpItem]
                    )
                    current_item_shop_count[PickMeUpItem] = max(
                        0, current_item_shop_count.get(PickMeUpItem, 0) - 1
                    )

                target_items: list[type[BaseItem] | None] = [
                    i for i in (target.items or []) if i is not None
                ]
                if len(target_items) >= 15:
                    duplicated = [
                        i
                        for i in target_items
                        if current_item_shop_count.get(i, 0) > 1
                    ]
                    dropped = random.choice(duplicated or target_items)
                    target_items.remove(dropped)
                    current_item_shop_count[dropped] = max(
                        0, current_item_shop_count.get(dropped, 0) - 1
                    )
                target_items.append(PickMeUpItem)
                target.set_items(target_items)
                current_item_shop_count[PickMeUpItem] = (
                    current_item_shop_count.get(PickMeUpItem, 0) + 1
                )

    elif pickmeups == PickMeUpOptions.DEFAULT:
        may_guarantee = True
        if quality == ShopQualities.ORIGINAL:
            original_pickmeup_shops = original_item_shop_count.get(PickMeUpItem, 0)
            current_pickmeup_shops = current_item_shop_count.get(PickMeUpItem, 0)
            may_guarantee = (
                original_pickmeup_shops > 0
                and current_pickmeup_shops < original_pickmeup_shops
            )

        has_pickmeup = any(
            shop is not None and PickMeUpItem in (shop.items or [])
            for shop in world.shops.shops
        )

        if may_guarantee and not has_pickmeup:
            eligible_shops = [
                shop
                for shop in world.shops.shops
                if shop is not None
                and shop.index != FROG_DISCIPLE_SHOP
                and original_shop_data.get(shop.index, {}).get("has_consumable", False)
                and len(shop.items or []) < 15
                and PickMeUpItem not in (shop.items or [])
            ]

            if eligible_shops:
                target = random.choice(eligible_shops)
                target_items = [i for i in (target.items or []) if i is not None]
                target_items.append(PickMeUpItem)
                target.set_items(target_items)
                current_item_shop_count[PickMeUpItem] = (
                    current_item_shop_count.get(PickMeUpItem, 0) + 1
                )

    if free_shops:
        for item in world.items.items:
            if item.price > 0:
                item.set_price(1)

    lower_tier_items = [
        MushroomItem,
        MidMushroomItem,
        HoneySyrupItem,
        MapleSyrupItem,
        AbleJuiceItem,
        BracerItem,
        EnergizerItem,
        YoshiCookieItem,
        PureWaterItem,
        YoshiCandyItem,
        FroggieDrinkItem,
        MukuCookieItem,
        ElixirItem,
        FreshenUpItem,
        MushroomItem2,
    ]
    if not no_pickmeups:
        lower_tier_items.append(PickMeUpItem)
    higher_tier_items = [
        MaxMushroomItem,
        RoyalSyrupItem,
        YoshiAdeItem,
        RedEssenceItem,
        KerokeroColaItem,
        MegalixirItem,
        RockCandyItem,
        CrystallineItem,
        PowerBlastItem,
    ]

    low_item = cast(Item, world.get_item(random.choice(lower_tier_items)))
    high_item = cast(Item, world.get_item(random.choice(higher_tier_items)))

    world.room_service_items = [type(low_item), type(high_item)]

    low_price = low_item.room_service_price
    high_price = high_item.room_service_price
    world.room_service_prices = [low_price, high_price]

    updates = zip(
        ["room_service_price_1_a", "room_service_price_1_b", "room_service_item_id_1",
         "room_service_price_2_a", "room_service_price_2_b", "room_service_item_id_2"],
        [low_price, low_price, type(low_item),
         high_price, high_price, type(high_item)]
    )
    for identifier, val in updates:
        cmd = world.event_scripts.get_command_by_identifier(identifier, SetVarToConst)
        assert cmd is not None, f"Event script command with identifier '{identifier}' not found"
        var = cmd.address
        cmd.set_value_and_address(var, val)

    if not free_shops:
        frog_coin_items = frog_disciple_set | frog_emporium_items

        for item_type in frog_coin_items:
            if item_type is None:
                continue
            if item_type in ORIGINAL_FROG_COIN_ITEMS:
                continue
            item = world.items.get_by_type(item_type)
            if item and item.price > 0:
                item.set_price(max(1, item.price // frog_coins_per_coin(item)))

        for item_type in ORIGINAL_FROG_COIN_ITEMS:
            if item_type in frog_coin_items:
                continue
            item = world.items.get_by_type(item_type)
            if item and item.price > 0:
                item.set_price(min(9999, item.price * frog_coins_per_coin(item)))

    for shop in world.shops.shops:
        if shop is None:
            continue
        current_items = [item for item in (shop.items or []) if item is not None]
        sorted_items = sorted(
            current_items,
            key=lambda item_type: (0 if item_type().item_id >= 96 else 1, item_type().item_id)  # type: ignore
        )
        shop.set_items(sorted_items)

    bomb_pool = [
        IceBombItem,
        FireBombItem,
        SleepyBombItem,
        FrightBombItem,
        RockCandyItem,
        BadMushroomItem
    ]

    bi = [cast(Item, world.get_item(b)) for b in random.sample(bomb_pool, 3)]

    world.bomb_shop_items = [type(b) for b in bi]

    bomb_updates = zip(
        ["bomb_shop_item_1", "bomb_shop_item_2", "bomb_shop_item_3"],
        [type(b) for b in bi]
    )
    for identifier, val in bomb_updates:
        cmd = world.event_scripts.get_command_by_identifier(identifier, SetVarToConst)
        assert cmd is not None, f"Event script command with identifier '{identifier}' not found"
        var = cmd.address
        cmd.set_value_and_address(var, val)
    
    