# Item/shop randomization logic

import random

from randomizer.data import items
from randomizer.data.characters import Mario, Mallow, Geno, Bowser, Peach
from . import flags, utils


def _randomize_item(item):
    """Perform randomization for an item.  Non-equipment will not be shuffled (price is done in the shop logic).

    Args:
        item(randomizer.data.items.Item):
    """
    if not item.is_equipment:
        return

    if item.world.settings.is_flag_enabled(flags.EquipmentStats):
        # Randomize number of attributes to go up or down. Guarantee >= 1 attribute goes up, but none go down.
        # For each set, 1/3 chance all non-zero ones go up/down.  Otherwise, weighted random number of stats.
        # ...attributes going up
        ups = []
        if random.randint(1, 3) == 1:
            ups = [attr for attr in item.EQUIP_STATS if getattr(item, attr) > 0]

        if not ups:
            num_up = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 10, 5, 1])[0]
            while True:
                ups = random.sample(item.EQUIP_STATS, num_up)
                if set(ups) & set(item.primary_stats):
                    break

        # ...attributes going down
        if random.randint(1, 3) == 1:
            downs = [attr for attr in item.EQUIP_STATS if getattr(item, attr) >= 128]
        else:
            num_down = random.choices([0, 1, 2, 3, 4, 5], weights=[1, 5, 10, 10, 5, 1])[0]
            downs = random.sample(item.EQUIP_STATS, num_down)

        # Give priority to going up if a stat was picked to go up.
        downs = [d for d in downs if d not in ups]

        # Track increases and decreases for each stat.
        score = item.stat_point_value
        up_vals = dict([(u, 0) for u in ups])
        down_vals = dict([(d, 0) for d in downs])

        # For attributes going down, randomize a number of points to decrease based on the total item score.
        # Distribution is weighted towards the lower half of the range.
        if downs:
            if score != 0:
                down_points = random.randint(0, random.randint(0, score))
            else:
                down_points = random.randint(0, random.randint(0, random.randint(0, 100)))

            # Spread number of "down points" randomly across stats being decreased.  Add this number of points to
            # the "score" of the item so we add stat increases to compensate.
            score += down_points
            for _ in range(down_points):
                attr = random.choice(downs)
                down_vals[attr] += 1

        # Spread number of "up points" randomly across stats being increased.  Treat non-primary stat increase as
        # two points to match the item score calculation.
        while score > 0:
            attr = random.choice(ups)
            up_vals[attr] += 1
            if attr in item.primary_stats:
                score -= 1
            else:
                score -= 2

        # Zero all stats.
        for attr in item.EQUIP_STATS:
            setattr(item, attr, 0)

        # Perform standard mutation on new non-zero stats.
        for attr in up_vals:
            setattr(item, attr, utils.mutate_normal(up_vals[attr], minimum=1, maximum=127))

        for attr in down_vals:
            value = utils.mutate_normal(down_vals[attr], minimum=1, maximum=127)
            setattr(item, attr, -value)

        # If this is a weapon with a variance value, shuffle that too.
        if item.variance:
            item.variance = utils.mutate_normal(item.variance, minimum=1, maximum=127)

    if item.world.settings.is_flag_enabled(flags.EquipmentCharacters):
        # Randomize which characters can equip this item.
        # Geno can only equip his own weapons, and nobody else can equip his due to softlocks.
        if not item.is_weapon or Geno not in item.equip_chars:
            # Pick random number of characters with lower numbers weighted heavier.
            new_chars = set()
            num_equippable = random.randint(1, random.randint(1, 5))

            for _ in range(num_equippable):
                char_choices = {Mario, Mallow, Geno, Bowser, Peach} - new_chars

                # Mario cannot equip Hurly Gloves due to softlock when he throws himself.
                if isinstance(item, items.HurlyGloves) and Mario in char_choices:
                    char_choices.remove(Mario)

                # Geno can only equip his own weapons (we checked if this was one of his above).
                if item.is_weapon and Geno in char_choices:
                    char_choices.remove(Geno)

                if not char_choices:
                    break

                # Now choose a random character to be equipable.
                char_choices = sorted(char_choices, key=lambda c: c.index)
                new_chars.add(random.choice(char_choices))

            item.equip_chars = list(new_chars)

    # Shuffle special properties.
    if item.world.settings.is_flag_enabled(flags.EquipmentBuffs):
        if item.tier == 1:
            odds = 2 / 3
        elif item.tier == 2:
            odds = 1 / 2
        elif item.tier == 3:
            odds = 1 / 4
        elif item.tier == 4:
            odds = 1 / 8
        elif item.tier == 5:
            odds = 1 / 16
        else:
            odds = 0

        # 7.1.3 update: trying lower odds for special properties and buffs, they're too frequent...
        odds /= 2

        if odds > 0:
            # Instant KO protection.
            item.prevent_ko = utils.coin_flip(odds)

            # Elemental immunities.
            item.elemental_immunities = []
            for i in range(4, 7):
                if utils.coin_flip(odds):
                    item.elemental_immunities.append(i)

            # Elemental resistances (don't add if we're already immune).
            item.elemental_resistances = []
            for i in range(4, 7):
                if i not in item.elemental_immunities and utils.coin_flip(odds):
                    item.elemental_resistances.append(i)

            # For certain namesake items, keep their status immunities so people don't get confused for safety.
            guaranteed_immunities = []
            if (isinstance(item, (items.FearlessPin, items.AntidotePin, items.TrueformPin, items.WakeUpPin)) and
                    not item.world.settings.is_flag_enabled(flags.EquipmentNoSafetyChecks)):
                guaranteed_immunities = item.status_immunities

            # Status immunities.
            item.status_immunities = []
            for i in range(0, 7):
                # Skip berserk status if the safety checks on enemy shuffle is not enabled.
                if i == 4 and not item.world.settings.is_flag_enabled(flags.EnemyNoSafetyChecks):
                    continue

                if utils.coin_flip(odds):
                    item.status_immunities.append(i)

            # Add guaranteed immunities back.
            for i in guaranteed_immunities:
                if i not in item.status_immunities:
                    item.status_immunities.append(i)

            # Weight weapons more towards the status buffs, and weight armor/accessories towards immunities.
            # For a special set of accessories, keep status buff odds the same as tier:
            # Jinx Belt, Attack Scarf, Quartz Charm, Troopa Pin, Feather, Ghost Medal, Jump Shoes, Zoom Shoes
            if item.index in (74, 76, 81, 89, 90, 91, 92, 94):
                buff_odds = 1
            elif item.is_weapon:
                buff_odds = 1 / 2
            else:
                buff_odds = 1 / 5

            # Status buffs.
            item.status_buffs = []
            for i in range(3, 7):
                if utils.coin_flip(odds * buff_odds):
                    item.status_buffs.append(i)


def randomize_all(world):
    """Randomize everything for items for a single seed.

    :type world: randomizer.logic.main.GameWorld
    """
    # Shuffle equipment stats and equip characters.
    for item in world.items:
        _randomize_item(item)

    # Safety check that at least four tier equips have instant death protection for safety.
    if (world.settings.is_flag_enabled(flags.EquipmentBuffs) and
            not world.settings.is_flag_enabled(flags.EquipmentNoSafetyChecks)):
        instant_ko_items = len([item for item in world.items if item.prevent_ko])
        if instant_ko_items < 4:
            top_armor = [item for item in world.items if (item.is_armor or item.is_accessory) and item.tier == 1 and
                         not item.prevent_ko]
            for item in random.sample(top_armor, 4 - instant_ko_items):
                item.prevent_ko = True

    # Shuffle shop contents and prices.
    if world.settings.is_flag_enabled(flags.ShopShuffle):
        assignments = {}

        # ******************************* Phase 1: Frog coin shops
        # Allow rare items, consumables, and accessories to be in frog coin shops.
        frog_candidates = [i for i in world.items if i.price and (i.rare or i.consumable or i.is_accessory)]
        frog_not_rare = [i for i in frog_candidates if not i.rare]

        # Pick some random not-rare items to not include in the frog coin shops.
        unfrog = random.randint(random.randint(0, len(frog_not_rare)), len(frog_not_rare))
        unfrog = random.sample(frog_not_rare, unfrog)

        for i in sorted(unfrog, key=lambda i2: i2.index):
            frog_candidates.remove(i)

        # Pick 25 items to be in the frog coin shops total.
        frog_chosen = random.sample(frog_candidates, 25)

        # Get list of items where only one is needed for disciple shop: only one character can equip, or it's reuseable.
        one_only = [i for i in frog_chosen if
                    (i.is_equipment and len(i.equip_chars) == 1) or
                    (i.consumable and i.reuseable)]

        # Choose some number of single items for the disciple shop, max of 10.
        num_choose = min(10, len(one_only))
        num_choose = random.randint(random.randint(0, num_choose), num_choose)
        num_choose = min(num_choose, len(one_only))
        chosen = random.sample(one_only, num_choose)

        # If we have less than 10 items chosen, include other equipment in the mix and choose some more.
        choose_again = [i for i in frog_chosen if i not in chosen and (i in one_only or i.is_equipment)]

        num_choose = 10 - len(chosen)
        num_choose = random.randint(random.randint(0, num_choose), num_choose)
        num_choose = min(num_choose, len(choose_again))

        if num_choose and choose_again:
            chosen += random.sample(choose_again, num_choose)

        # If we still have less than 10 items chosen, fill in the remaining slots with any remaining frog coin items.
        num_choose = 10 - len(chosen)
        if num_choose:
            choose_again = [i for i in frog_chosen if i not in chosen]
            random.shuffle(choose_again)
            chosen += choose_again[:num_choose]

        # Sanity check
        if len(chosen) != 10:
            raise ValueError("Wrong number of items chosen for disciple shop - {}".format(len(chosen)))

        # Put the chosen 10 in the disciple shop and the remaining 15 in the emporium.
        assignments[items.DiscipleShop.index] = chosen
        assignments[items.FrogCoinEmporiumShop.index] = [i for i in frog_chosen if i not in chosen]

        # ******************************* Phase 2: Non-frog coin shops
        # Carry over a random number of left-over frog coin candidates.
        carryover = [i for i in frog_candidates if
                     i not in assignments[items.DiscipleShop.index] and
                     i not in assignments[items.FrogCoinEmporiumShop.index]]
        num_choose = random.randint(0, random.randint(0, len(carryover)))
        carryover = random.sample(carryover, num_choose)

        # Take carryover items, plus any non-rare items that aren't already in the frog coin shops, and sort by rank.
        shop_items = carryover + [i for i in world.items if
                                  i not in assignments[items.DiscipleShop.index] and
                                  i not in assignments[items.FrogCoinEmporiumShop.index] and
                                  not i.rare]
        shop_items = sorted(set(shop_items), key=lambda i: i.rank)

        done_already = set()
        for shop in world.shops:
            # Skip partial juice bar lists and frog coin shops.
            if isinstance(shop, items.PartialJuiceBarShop) or shop.frog_coin_shop:
                continue

            # For the full juice bar, make it always the full 15 items.  For other shops, randomize the number.
            if shop.index == 12:
                num_items = 15
            else:
                num_items = len(shop.items)
                num_items = utils.mutate_normal(num_items, minimum=1, maximum=15)

            # Filter valid items by special conditions for this shop, if any.
            valid_items = [i for i in shop_items if shop.is_item_allowed(i)]

            # Remove items that were already placed in other shops, but allow basic consumables to be reused.
            # Don't do this for the full juice bar list, or the baby Goomba's shop in Monstro Town.
            if shop.index not in [12, 13, 14, 20]:
                potential_items = [i for i in valid_items if i not in done_already or
                                   (i.consumable and not i.reuseable and not i.rare and i.basic)]
                if potential_items:
                    valid_items = sorted(potential_items, key=lambda i: i.rank)

            # Sanity check
            if not valid_items:
                raise ValueError("No valid items for shop {}".format(shop.index))

            num_items = min(num_items, len(valid_items))

            # If we have more valid items than what the shop will hold, split into consumable and non-consumable items
            # and take a random sample of both, so we get some consumables across all shops.
            if shop.index != 20 and len(valid_items) > num_items:
                valid_items = valid_items[:random.randint(num_items, random.randint(num_items, len(valid_items)))]
                consumables = [i for i in valid_items if i.consumable]
                others = [i for i in valid_items if i not in consumables]
                if consumables and others and num_items >= 4:
                    num_con = (random.randint(0, num_items) + random.randint(0, num_items)) // 2
                    num_con = max(num_con, num_items - num_con)
                    num_con = min(num_con, num_items - 2)
                    num_oth = num_items - num_con
                    num_con = min(num_con, len(consumables))
                    num_oth = min(num_oth, len(others))
                    valid_items = (random.sample(consumables, num_con) + random.sample(others, num_oth))
                    num_items = num_con + num_oth

            # Choose the final list of items from the valid ones.
            chosen_items = random.sample(valid_items, num_items)
            assignments[shop.index] = chosen_items
            for i in chosen_items:
                done_already.add(i)

        # Build the partial juice bar lists by taking a random sample of the next bigger list, working backwards.
        for n, p in enumerate([items.JuiceBarPartial3, items.JuiceBarPartial2, items.JuiceBarPartial1]):
            n = 3 - n
            previous_items = assignments[p.index + 1]
            minimum = n
            maximum = len(previous_items) - 1
            average = (minimum + maximum) // 2
            if not (minimum <= average <= maximum):
                raise RuntimeError("Bad number of items for partial juice bar {}: assignments {}".format(
                    p, assignments))
            num_items = random.randint(random.randint(minimum, average), maximum)
            chosen_items = random.sample(previous_items, num_items)
            assignments[p.index] = chosen_items

        # ******************************* Phase 3: Repricing
        repriced = set()
        for shop in world.shops:
            assigned_items = assignments[shop.index]
            for item in assigned_items:
                # If we already repriced the item, skip it.
                if item in repriced:
                    continue

                # Turn the item into a frog coin price if it's in one of those shops.
                if shop.frog_coin_shop:
                    item.become_frog_coin_item()
                else:
                    # If the item is already not a frog coin item and it's rare, use max(price, rank) as the base price.
                    if not item.unbecome_frog_coin_item() and item.rare:
                        item.price = max(item.price, int(item.rank))

                # Shuffle the final computed price.
                price = min(9999, max(2, item.price))
                price = utils.mutate_normal(price, minimum=2, maximum=9999)
                item.price = price
                repriced.add(item)

        # Sort the list of items by the ordering rank for display, and assign to the shop.
        for shop in world.shops:
            shop.items = sorted(assignments[shop.index], key=lambda i: i.order)
