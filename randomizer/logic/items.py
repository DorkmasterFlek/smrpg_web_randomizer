# Item/shop randomization logic

import random

from . import utils
from .patch import Patch

# Stats used during equipment randomization.
EQUIP_STATS = ["speed", "attack", "defense", "magic_attack", "magic_defense"]


class Item:
    """Class representing an item."""
    BASE_ADDRESS = 0x3a014d
    BASE_PRICE_ADDRESS = 0x3a40f2

    def __init__(self, index, name, order, item_type, consumable, reuseable, equip_chars, speed, attack, defense,
                 magic_attack, magic_defense, variance, price, frog_coin_item, rare, basic):
        """
        :type index: int
        :type name: str
        :type order: int
        :type item_type: int
        :type consumable: bool
        :type reuseable: bool
        :type equip_chars: list[int]
        :type speed: int
        :type attack: int
        :type defense: int
        :type magic_attack: int
        :type magic_defense: int
        :type variance: int
        :type price: int
        :type frog_coin_item: bool
        :type rare: bool
        :type basic: bool
        """
        self.index = index
        self.name = name
        self.order = order
        self.item_type = item_type
        self.consumable = consumable
        self.reuseable = reuseable
        self.equip_chars = equip_chars
        self.speed = speed
        self.attack = attack
        self.defense = defense
        self.magic_attack = magic_attack
        self.magic_defense = magic_defense
        self.variance = variance
        self.price = price
        self.frog_coin_item = frog_coin_item
        self.rare = rare
        self.basic = basic

    @property
    def is_weapon(self):
        """:rtype: bool"""
        return self.item_type & 0x3 == 0

    @property
    def is_armor(self):
        """:rtype: bool"""
        return self.item_type & 0x3 == 1

    @property
    def is_accessory(self):
        """:rtype: bool"""
        return self.item_type & 0x3 == 2

    @property
    def is_equipment(self):
        """:rtype: bool"""
        return self.is_weapon or self.is_armor or self.is_accessory

    @property
    def is_consumable(self):
        """:rtype: bool"""
        return self.consumable

    @property
    def is_reusable(self):
        """:rtype: bool"""
        return self.reuseable

    @property
    def is_key(self):
        """:rtype: bool"""
        return not (self.is_equipment or self.is_consumable)

    @property
    def is_frog_coin_item(self):
        """:rtype: bool"""
        return self.frog_coin_item

    def become_frog_coin_item(self):
        """:rtype: bool"""
        if self.is_frog_coin_item:
            return False

        factor = float(random.randint(random.randint(10, 50), 50))
        if self.rare:
            price = int(round(self.rank / factor))
        else:
            price = int(round(self.price / factor))
        self.price = min(max(price, 1), 50)
        self.frog_coin_item = True
        return True

    def unbecome_frog_coin_item(self):
        """:rtype: bool"""
        if not self.is_frog_coin_item:
            return False

        factor = float(random.randint(50, random.randint(50, 100)))
        price = int(round(self.price * factor))
        self.price = min(price, 9999)
        self.frog_coin_item = False
        return True

    @property
    def primary_stats(self):
        """Primary stats of this item, depending on the type.

        :rtype: list[str]
        """
        if self.is_weapon:
            return ["attack"]
        elif self.is_armor:
            return ["defense", "magic_defense"]
        return EQUIP_STATS

    @property
    def stat_point_value(self):
        """Overall stat point score for rough item power during shuffle.

        :rtype: int
        """
        score = 0
        for attr in EQUIP_STATS:
            value = getattr(self, attr)
            # Subtract any negative value from overall score.
            if value < 0:
                score += value
            # For primary stat, add the raw value.
            elif attr in self.primary_stats:
                score += value
            # If item has positive stat outside of primary stats, consider that double points for the score.
            else:
                score += (2 * value)
        return score

    @property
    def rank(self):
        """Compute a ranking for this item based on price and type.  Used for shuffling shops.

        :rtype: float
        """
        if hasattr(self, "_rank"):
            return self._rank

        if self.price == 0 and not self.is_key:
            self._rank = random.randint(1, random.randint(1, 999))
        elif self.price == 0:
            self._rank = -1
        elif self.is_frog_coin_item:
            self._rank = self.price * 50
        elif self.price > 1000:
            self._rank = self.price / 2
        elif self.rare and self.is_consumable:
            rank = 2 * self.price
            if self.price <= 50:
                rank = rank * 50
            if self.reuseable:
                rank = rank * 4
            self._rank = rank
        elif self.rare and self.is_armor:
            self._rank = self.price * 3
        elif self.index == 0x5e:  # quartz charm
            self._rank = 999
        elif self.rare and self.is_accessory:
            self._rank = self.price * 2
        else:
            self._rank = self.price

        # Add a small amount based on index so items with the same overall rank will be sorted by index.
        self._rank += self.index / 1000.0
        return self.rank

    def get_similar(self, candidates):
        """Get a random similar item from a list of potential candidates for this one.

        :type candidates: list[Item]
        :rtype: Item
        """
        # If this is a special item, don't replace it.
        if self.rank < 0:
            return self
        elif self not in candidates:
            return self

        # Sort by rank and mutate our position within the list to get a replacement item.
        candidates = sorted(candidates, key=lambda c: c.rank)
        index = candidates.index(self)
        index = utils.mutate_normal(index, maximum=len(candidates) - 1)
        return candidates[index]

    def randomize(self):
        """Perform randomization for equipment.  Other items will not be shuffled (price is done in the shop logic)."""
        if not self.is_equipment:
            return

        # Randomize number of attributes to go up or down. Guarantee >= 1 attribute will go up, but none could go down.
        # For each set, 1/3 chance all non-zero ones go up/down.  Otherwise, weighted random number centered around 2-3.
        # ...attributes going up
        ups = []
        if random.randint(1, 3) == 1:
            ups = [attr for attr in EQUIP_STATS if getattr(self, attr) > 0]

        if not ups:
            num_up = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 10, 5, 1])[0]
            while True:
                ups = random.sample(EQUIP_STATS, num_up)
                if set(ups) & set(self.primary_stats):
                    break

        # ...attributes going down
        if random.randint(1, 3) == 1:
            downs = [attr for attr in EQUIP_STATS if getattr(self, attr) >= 128]
        else:
            num_down = random.choices([0, 1, 2, 3, 4, 5], weights=[1, 5, 10, 10, 5, 1])[0]
            downs = random.sample(EQUIP_STATS, num_down)

        # Give priority to going up if a stat was picked to go up.
        downs = [d for d in downs if d not in ups]

        # Track increases and decreases for each stat.
        score = self.stat_point_value
        up_vals = dict([(u, 0) for u in ups])
        down_vals = dict([(d, 0) for d in downs])

        # For attributes going down, randomize a number of points to decrease based on the total item score.
        # Distribution is weighted towards the lower half of the range.
        if downs:
            if score != 0:
                down_points = random.randint(0, random.randint(0, score))
            else:
                down_points = random.randint(0, random.randint(0, random.randint(0, 100)))

            # Spread number of "down points" randomly across stats being decreased.  Add this number of points to the
            # "score" of the item so we add stat increases to compensate.
            score += down_points
            for _ in range(down_points):
                attr = random.choice(downs)
                down_vals[attr] += 1

        # Spread number of "up points" randomly across stats being increased.  Treat non-primary stat increase as two
        # points to match the item score calculation.
        while score > 0:
            attr = random.choice(ups)
            up_vals[attr] += 1
            if attr in self.primary_stats:
                score -= 1
            else:
                score -= 2

        # Zero all stats.
        for attr in EQUIP_STATS:
            setattr(self, attr, 0)

        # Perform standard mutation on new non-zero stats.
        for attr in up_vals:
            setattr(self, attr, utils.mutate_normal(up_vals[attr], minimum=1, maximum=127))

        for attr in down_vals:
            value = utils.mutate_normal(down_vals[attr], minimum=1, maximum=127)
            setattr(self, attr, -value)

        # If this is a weapon with a variance value, shuffle that too.
        if self.variance:
            self.variance = utils.mutate_normal(self.variance, minimum=1, maximum=127)

        # Randomize which characters can equip this item.
        # Geno can only equip his own weapons, and nobody else can equip his due to softlocks.
        if self.is_weapon and 3 in self.equip_chars:
            return

        # Pick random number of characters with lower numbers weighted heavier.
        new_chars = set()
        num_equippable = random.randint(1, random.randint(1, 5))

        for _ in range(num_equippable):
            char_choices = set(range(5)) - new_chars

            # Mario cannot equip Hurly Gloves due to softlock when he throws himself.
            if self.index == 0x14 and 0 in char_choices:
                char_choices.remove(0)

            # Geno can only equip his own weapons (we checked if this was one of his above).
            if self.is_weapon and 3 in char_choices:
                char_choices.remove(3)

            if not char_choices:
                break

            # Now choose a random character to be equipable.
            char_choices = sorted(char_choices)
            new_chars.add(random.choice(char_choices))

        self.equip_chars = list(new_chars)

    def get_patch(self):
        """Get patch for this item.

        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()
        base_addr = self.BASE_ADDRESS + (self.index * 18)

        # For non-shop items with no price (key items), there is no randomization.
        if not self.price:
            return patch

        # Which characters can equip
        patch.add_data(base_addr + 2, utils.BitMapSet(1, self.equip_chars).as_bytes())

        # Stat data
        data = bytearray()
        data += utils.ByteField(self.speed).as_bytes()
        data += utils.ByteField(self.attack).as_bytes()
        data += utils.ByteField(self.defense).as_bytes()
        data += utils.ByteField(self.magic_attack).as_bytes()
        data += utils.ByteField(self.magic_defense).as_bytes()
        data += utils.ByteField(self.variance).as_bytes()
        patch.add_data(base_addr + 9, data)

        # Price
        price_addr = self.BASE_PRICE_ADDRESS + (self.index * 2)
        patch.add_data(price_addr, utils.ByteField(self.price, num_bytes=2).as_bytes())

        return patch


class Shop:
    """Class representing a shop with a list of items."""
    BASE_ADDRESS = 0x3a44df

    def __init__(self, index, frog_coin_shop, items):
        """
        :type index: int
        :type frog_coin_shop: bool
        :type items: list[Item]
        """
        self.index = index
        self.frog_coin_shop = frog_coin_shop
        self.items = items

    @property
    def rank(self):
        """Rank for the shop based on highest priced item for balancing.

        :rtype: int
        """
        maxprice = max([i.price for i in self.items])
        if self.frog_coin_shop:
            maxprice += 2000
        return maxprice

    @property
    def is_juice_bar(self):
        """:rtype: bool"""
        return 0x9 <= self.index <= 0xc

    def get_patch(self):
        """Get patch for this shop.

        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()
        base_addr = self.BASE_ADDRESS + (self.index * 16)

        data = bytearray()
        for item in self.items:
            data += utils.Stat(item.index).as_bytes()

        # Fill out extra shop fields with no item value.
        while len(data) < 15:
            data += utils.Stat(255).as_bytes()

        # First byte is shop flags, don't change those.  Put items one byte later.
        patch.add_data(base_addr + 1, data)

        return patch


def randomize_items(world):
    """Randomize everything for items for a single seed.

    :type world: randomizer.logic.main.GameWorld
    """
    # Shuffle equipment stats and equip characters.
    if world.settings.randomize_equipment:
        for item in world.items:
            item.randomize()

    # Shuffle shop contents and prices.
    if world.settings.randomize_shops:
        assignments = {}

        # ******************************* Phase 1: Frog coin shops
        # Allow rare items, consumables, and accessories to be in frog coin shops.
        frog_candidates = [i for i in world.items if i.price and (i.rare or i.is_consumable or i.is_accessory)]
        frog_not_rare = [i for i in frog_candidates if not i.rare]

        # Pick some random not-rare items to not include in the frog coin shops.
        unfrog = random.randint(random.randint(0, len(frog_not_rare)), len(frog_not_rare))
        unfrog = random.sample(frog_not_rare, unfrog)

        for i in sorted(unfrog, key=lambda i2: i2.index):
            frog_candidates.remove(i)

        # Pick 25 items to be in the frog coin shops total.
        frog_chosen = random.sample(frog_candidates, 25)
        disciple_shop = 3
        frog_coin_emporium = 6

        # Get list of items where only one is needed for disciple shop: only one character can equip, or it's reuseable.
        one_only = [i for i in frog_chosen if
                    (i.is_equipment and len(i.equip_chars) == 1) or
                    (i.is_consumable and i.reuseable)]

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
        assignments[disciple_shop] = chosen
        assignments[frog_coin_emporium] = [i for i in frog_chosen if i not in chosen]

        # ******************************* Phase 2: Non-frog coin shops
        # Carry over a random number of left-over frog coin candidates.
        carryover = [i for i in frog_candidates if
                     i not in assignments[disciple_shop] and
                     i not in assignments[frog_coin_emporium]]
        num_choose = random.randint(0, random.randint(0, len(carryover)))
        carryover = random.sample(carryover, num_choose)

        # Take carryover items, plus any non-rare items that aren't already in the frog coin shops, and sort by rank.
        shop_items = carryover + [i for i in world.items if
                                  i not in assignments[disciple_shop] and
                                  i not in assignments[frog_coin_emporium] and
                                  not i.rare]
        shop_items = sorted(set(shop_items), key=lambda i: i.rank)

        # Partial juice bar lists for the alto/teno/soprano cards, and the first characters to join for balancing.
        juice_bar_partial = [9, 10, 11]  # full: 12
        first_two_chars = set([0] + [c.index for c in world.character_join_order[:1]])
        first_three_chars = set([0] + [c.index for c in world.character_join_order[:2]])

        # Define conditions for some shops to balance the item distribution.
        # ex. Make sure equipment in the first couple shops is actually equipable by the first characters to join.
        special_conditions = {
            0: lambda i: i.is_consumable or (i.is_equipment and (set(i.equip_chars) & first_two_chars)),
            1: lambda i: i.is_consumable,
            2: lambda i: i.is_equipment and (set(i.equip_chars) & first_three_chars),
            4: lambda i: i.is_consumable or (i.is_equipment and (set(i.equip_chars) & first_three_chars)),
            # Don't put any basic (healing) items in the bomb shop because it disappears.
            8: lambda i: i.is_consumable and not i.basic,
            12: lambda i: special_conditions[8](i) and not i.reuseable,
            # Seaside weapon shop
            13: lambda i: i.is_weapon,
            # Seaside armor shop
            14: lambda i: i.is_armor,
            15: lambda i: i.is_accessory,
            16: lambda i: i.is_consumable,
            18: lambda i: i.is_consumable,
            19: lambda i: i.is_equipment,
            20: lambda i: special_conditions[8](i),
            24: lambda i: i.is_consumable,
        }

        done_already = set()
        for shop in world.shops:
            # Skip partial juice bar lists and frog coin shops.
            if shop.index in juice_bar_partial + [disciple_shop, frog_coin_emporium]:
                continue

            # For the full juice bar, make it always the full 15 items.  For other shops, randomize the number.
            if shop.index == 12:
                num_items = 15
            else:
                num_items = len(shop.items)
                num_items = utils.mutate_normal(num_items, minimum=1, maximum=15)

            # Filter valid items by special conditions for this shop, if any.
            valid_items = list(shop_items)
            if shop.index in special_conditions:
                valid_items = [i for i in valid_items if special_conditions[shop.index](i)]

            # Remove items that were already placed in other shops, but allow basic consumables to be reused.
            # Don't do this for the full juice bar list, or the baby goomba's shop in Monstro Town.
            if shop.index not in [12, 13, 14, 20]:
                potential_items = [i for i in valid_items if i not in done_already or
                                   (i.is_consumable and not i.reuseable and not i.rare and i.basic)]
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
                consumables = [i for i in valid_items if i.is_consumable]
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
        for n, p in enumerate(sorted(juice_bar_partial, reverse=True)):
            n = len(juice_bar_partial) - n
            previous_items = assignments[p + 1]
            minimum = n
            maximum = len(previous_items) - 1
            average = (minimum + maximum) // 2
            num_items = random.randint(random.randint(minimum, average), maximum)
            chosen_items = random.sample(previous_items, num_items)
            assignments[p] = chosen_items

        # ******************************* Phase 3: Repricing
        repriced = set()
        for shop in world.shops:
            assigned_items = assignments[shop.index]
            for item in assigned_items:
                # If we already repriced the item, skip it.
                if item in repriced:
                    continue

                # Turn the item into a frog coin price if it's in one of those shops.
                if shop.index in [disciple_shop, frog_coin_emporium]:
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
