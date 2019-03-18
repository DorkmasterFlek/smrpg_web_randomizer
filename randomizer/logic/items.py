# Item/shop randomization logic

import random
import math

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
        # Old linear mode logic: Geno can only equip his own weapons, and nobody else can equip his due to softlocks!
        # This is fixed in open mode.
        if item.world.open_mode or (not item.is_weapon or Geno not in item.equip_chars):
            # Pick random number of characters with lower numbers weighted heavier.
            new_chars = set()
            num_equippable = random.randint(1, random.randint(1, 5))

            for _ in range(num_equippable):
                char_choices = {Mario, Mallow, Geno, Bowser, Peach} - new_chars

                # Linear mode: Geno can only equip his own weapons (we checked if this was one of his above).
                if not item.world.open_mode and item.is_weapon and Geno in char_choices:
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
        
    for item in world.items:
        if item.is_equipment:
            if item.index in (83, 148, 93):
                item.arbitrary_value = 1
            elif item.index == 88:
                item.arbitrary_value = 2
            elif item.index in (76, 79):
                item.arbitrary_value = 1
            elif item.index == 80:
                item.arbitrary_value = 10
            item.rank_value = item.attack * max(0, min(2, (item.attack + item.variance) / (1 if (item.attack - item.variance == 0) else (item.attack - item.variance)))) + max (0, (item.magic_attack / (2 if item.magic_attack < 0 else 1)) + (item.magic_defense / (2 if item.magic_defense < 0 else 1)) + (item.defense / (2 if item.defense < 0 else 1)) + min (20, item.speed / 2)) + 10 * len(item.status_immunities) + 15 * len(item.elemental_immunities) + 7.5 * len(item.elemental_resistances) + 50 * (1 if item.prevent_ko else 0) + 30 * len(item.status_buffs) + 10 * item.arbitrary_value

        #Calculate list position (used as a factor in pricing)
        ranks = [item for item in world.items if item.is_equipment]
        ranks.sort(key=lambda x: x.rank_value, reverse=True)
        ranks_reverse = sorted(ranks, key=lambda x: x.rank_value)

        for item in world.items:
            if item.is_equipment:
                item.rank_order = (ranks.index(item) + 1 if item in ranks else 0)
                item.rank_order_reverse = (ranks_reverse.index(item) + 1 if item in ranks_reverse else 0)
                if (item.rank_order <= 15):
                    item.hard_tier = 4
                elif (item.rank_order <= 35):
                    item.hard_tier = 3
                elif (item.rank_order <= 55):
                    item.hard_tier = 2
                else:
                    item.hard_tier = 1

    # Shuffle shop contents and prices.
    if world.settings.is_flag_enabled(flags.ShopShuffle):
        assignments = {}

        # ******************************* Phase 0: Calculate raw value to use as basis for pricing as well as Sb, Tb assignment

		# Calculate raw rank value

        if world.settings.is_flag_enabled(flags.ShopTierX):
            for shop in world.shops:
                shop.items = [i for i in world.items if i.index == 125]

        else:
            tiers_allowed = 4;
            if world.settings.is_flag_enabled(flags.ShopTier1):
                tiers_allowed = 1;
            elif world.settings.is_flag_enabled(flags.ShopTier2):
                tiers_allowed = 2;
            elif world.settings.is_flag_enabled(flags.ShopTier3):
                tiers_allowed = 3;


            #Always exclude special equips from shops if Mx is set
            if world.settings.is_flag_enabled(flags.MonstroExcludeElsewhere):
                for item in world.items:
                    if world.settings.is_flag_enabled(flags.MonstroTownLite):
                        if item.index in [69, 81, 89, 94, 90]:
                            item.hard_tier = 5
                    elif world.settings.is_flag_enabled(flags.MonstroTownHard):
                        if item.index in [69, 70, 74, 81, 89, 94, 90, 6, 11, 33]:
                            item.hard_tier = 5

            #Establish an array for each shop's items
            for shop in world.shops:
                assignments[shop.index] = []

            # ******************************* Phase 1: Frog coin shops

            #Sv
            if world.settings.is_flag_enabled(flags.ShopShuffleVanilla):
                #Sv and Sb - only allow the chosen highest tiers of items here
                if world.settings.is_flag_enabled(flags.ShopShuffleBalanced):
                    frog_candidates = [i for i in world.items if i.price and i.vanilla_shop and ((tiers_allowed <= 3 and i.hard_tier == tiers_allowed) or (tiers_allowed == 4 and i.hard_tier > 2 and i.hard_tier <= 4))]
                #No Sb - allow any item here, as long as permitted by tier exclusion flag
                else:
                    frog_candidates = [i for i in world.items if i.price and i.vanilla_shop and i.hard_tier <= tiers_allowed]
            #Sb only
            elif world.settings.is_flag_enabled(flags.ShopShuffleBalanced):
                #Only allow the chosen highest tiers of items here
                frog_candidates = [i for i in world.items if i.price and ((tiers_allowed <= 3 and i.hard_tier == tiers_allowed) or (tiers_allowed == 4 and i.hard_tier > 2 and i.hard_tier <= 4))]
            #Allow anything within tier exclusion flag
            else:
                frog_candidates = [i for i in world.items if i.price and i.hard_tier <= tiers_allowed]
            # Pick 25 items to be in the frog coin shops total.
            frog_chosen = random.sample(frog_candidates, min(len(frog_candidates), 25))
            disciple_shop = 3
            frog_coin_emporium = 6

            # Get list of items where only one is needed for disciple shop: only one character can equip, or it's reuseable.
            one_only = [i for i in frog_chosen if
                        (i.is_equipment and len(i.equip_chars) == 1) or
                        (i.consumable and i.reuseable)]
            # Choose 5-10.
            num_choose = min(10, len(one_only))
            num_choose = random.randint(min(0, num_choose), num_choose)
            chosen = random.sample(one_only, num_choose)
            # If we have less than 10 items chosen, include other equipment in the mix and choose some more.
            choose_again = [i for i in frog_chosen if i not in chosen and (i in one_only or i.is_equipment)]
            num_choose = 10 - len(chosen)
            num_choose = random.randint(0, num_choose)
            num_choose = min(num_choose, len(choose_again))
            if num_choose and choose_again:
                chosen += random.sample(choose_again, num_choose)

            # Put the chosen in the disciple shop and up to 15 remaining in the Emporium
            assignments[items.DiscipleShop.index] = chosen
            num_emporium = random.randint(random.randint(0, 15), 15)
            frog_remaining = [i for i in frog_chosen if i not in chosen]
            assignments[items.FrogCoinEmporiumShop.index] = random.sample(frog_remaining, num_emporium)

            # ******************************* Phase 2: Non-frog coin shops

            # Collect remaining items that aren't in frog coin shops and aren't key items.

            #exclude wallet, shiny stone, carbo cookie
            excluded_items =  [129, 137, 138]

            if world.settings.is_flag_enabled(flags.ShopShuffleVanilla):
                shop_items = [i for i in world.items if
                      i not in assignments[items.DiscipleShop.index] and
                      i not in assignments[items.FrogCoinEmporiumShop.index] and
                      i.price
                      and i.hard_tier <= tiers_allowed
                      and i.index not in excluded_items
                      and i.vanilla_shop]
            else:
                shop_items = [i for i in world.items if
                      i not in assignments[items.DiscipleShop.index] and
                      i not in assignments[items.FrogCoinEmporiumShop.index] and
                      i.price
                      and i.hard_tier <= tiers_allowed
                      and i.index not in excluded_items]

            #First, we want every item to wind up in a shop.
            done_already = set()
            #But we need a backup reserve of items to pull from in case the logic doesnt work out - i.e. Sb is enabled but there are no accessories in the upper tiers
            item_reserve = shop_items;

            #Unique items will first be split among the shops (anything except basic healing items)
            #unique_items = [i for i in shop_items if not (i.consumable and not i.reuseable and (i.hard_tier <= math.ceil(tiers_allowed / 2) or i.basic))]
            #basic_items = [i for i in shop_items if (i.consumable and not i.reuseable and (i.hard_tier <= math.ceil(tiers_allowed / 2) or i.basic))]
            unique_items = [i for i in shop_items if not (i.consumable and not i.reuseable and i.basic)]
            basic_items = [i for i in shop_items if (i.consumable and not i.reuseable and i.basic)]


            #Function determining what can go in a shop, based on flags selected
            def get_valid_items(base, shop, exclude=[]):
                #Sb and Sv
                if world.settings.is_flag_enabled(flags.ShopShuffleBalanced) and world.settings.is_flag_enabled(flags.ShopShuffleVanilla) and not world.settings.is_flag_enabled(flags.ShopTier1):
                    #Open shops
                    if (shop.index in [0, 1, 2, 4, 5, 7, 17, 20, 21] or (shop.index == 22 and world.settings.is_flag_enabled(flags.BowsersKeepOpen))):
                        valid_items = [i for i in base if i not in done_already and i.vanilla_shop and i not in exclude and shop.is_item_allowed(i) and (((tiers_allowed == 1 or tiers_allowed == 2) and i.hard_tier == 1) or ((tiers_allowed == 3 or tiers_allowed == 4) and i.hard_tier <= 2))]
                        #In case the equip shuffle logic works out so that nothing belongs in a tiered shop, pick any item of the appropriate class, ignoring tier
                        #if not valid_items:
                        #    valid_items = [i for i in base if i not in done_already and i.vanilla_shop and i not in exclude and shop.is_item_allowed(i)]
                    #Locked shops
                    elif (shop.index in [12, 13, 14, 15, 16, 18, 19, 23, 24] or (shop.index == 22 and not world.settings.is_flag_enabled(flags.BowsersKeepOpen))):
                        valid_items = [i for i in base if i not in done_already and i.vanilla_shop and shop.is_item_allowed(i) and ((tiers_allowed <= 3 and i.hard_tier == tiers_allowed) or (tiers_allowed == 4 and i.hard_tier > 2 and i.hard_tier <= 4))]
                        #if not valid_items:
                        #    valid_items = [i for i in base if i not in done_already and i.vanilla_shop and i not in exclude and shop.is_item_allowed(i)]
                    #Missable shop
                    elif (shop.index == 8):
                        valid_items = [i for i in base if shop.is_item_allowed(i) and i.vanilla_shop and i not in exclude and i.hard_tier <= tiers_allowed and not i.reuseable]
                #Sv only
                elif world.settings.is_flag_enabled(flags.ShopShuffleVanilla):
                    if (shop.index == 8):
                        valid_items = [i for i in base if shop.is_item_allowed(i) and i.vanilla_shop and i not in exclude and i.hard_tier <= tiers_allowed and not i.reuseable]
                    else:
                        valid_items = [i for i in base if i not in done_already and shop.is_item_allowed(i) and i.vanilla_shop and i not in exclude and i.hard_tier <= tiers_allowed]
                #Sb only
                elif world.settings.is_flag_enabled(flags.ShopShuffleBalanced) and not world.settings.is_flag_enabled(flags.ShopTier1):
                    #Open shops
                    if (shop.index in [0, 1, 2, 4, 5, 7, 17, 20, 21] or (shop.index == 22 and world.settings.is_flag_enabled(flags.BowsersKeepOpen))):
                        valid_items = [i for i in base if i not in done_already and i not in exclude and shop.is_item_allowed(i) and (((tiers_allowed == 1 or tiers_allowed == 2) and i.hard_tier == 1) or ((tiers_allowed == 3 or tiers_allowed == 4) and i.hard_tier <= 2))]
                        #if not valid_items:
                        #    valid_items = [i for i in base if i not in done_already and i not in exclude and i.vanilla_shop and shop.is_item_allowed(i)]
                    #Locked shops
                    elif (shop.index in [12, 13, 14, 15, 16, 18, 19, 23, 24] or (shop.index == 22 and not world.settings.is_flag_enabled(flags.BowsersKeepOpen))):
                        valid_items = [i for i in base if i not in done_already and i not in exclude and shop.is_item_allowed(i) and ((tiers_allowed <= 3 and i.hard_tier == tiers_allowed) or (tiers_allowed == 4 and i.hard_tier > 2 and i.hard_tier <= 4))]
                        #if not valid_items:
                        #    valid_items = [i for i in base if i not in done_already and i not in exclude and i.vanilla_shop and shop.is_item_allowed(i)]
                    #Missable shop
                    elif (shop.index == 8):
                        valid_items = [i for i in base if shop.is_item_allowed(i) and i not in exclude and i.hard_tier <= tiers_allowed and not i.reuseable]
                #Neither Sb nor Sv
                else:
                    if (shop.index == 8):
                        valid_items = [i for i in base if shop.is_item_allowed(i) and i not in exclude and i.hard_tier <= tiers_allowed and not i.reuseable]
                    else:
                        valid_items = [i for i in base if i not in done_already and i not in exclude and shop.is_item_allowed(i) and i.hard_tier <= tiers_allowed]
                return valid_items


            #Juice bar gets "first dibs"
            #This is kind of weird, but first partial juice bar is modeled after rose town shop since they have the same permission properties
            for shop1 in world.shops:
                if shop1.index == items.RoseTownItemShop.index:
                    jpshop = shop1
            for shop2 in world.shops:
                if shop2.index == items.JuiceBarFull.index:
                    jbshop = shop2
            #pick 1-4 of items exclusive to full bar
            possibleJB3 = get_valid_items(item_reserve, jbshop, assignments[12])
            if not (possibleJB3):
                partial4 = random.sample([i for i in basic_items if i not in assignments[12]], max(1,min(len(possibleJB3) - 2, random.randint(1, 4))))
            else:
                partial4 = random.sample(possibleJB3, max(1,min(len(possibleJB3) - 2, random.randint(1, 4))))
            for item in partial4:
                assignments[12].append(item)
                if (item in unique_items):
                    done_already.add(item)
            #pick a handful of items for third partial bar, include in full bar
            possibleJB2 = get_valid_items(item_reserve, jbshop, assignments[12])
            if not (possibleJB2):
                partial3 = random.sample([i for i in basic_items if i not in assignments[12]], max(1,min(len(possibleJB2) - 1, random.randint(1, 8 - len(partial4)))))
            else:
                partial3 = random.sample(possibleJB2, max(1,min(len(possibleJB2) - 1, random.randint(1, 8 - len(partial4)))))
            for item in partial3:
                assignments[11].append(item)
                assignments[12].append(item)
                if (item in unique_items):
                    done_already.add(item)
            #pick a handful of items for second partial bar, include in third and full bar
            possibleJB = get_valid_items(item_reserve, jbshop, assignments[12])
            if not (possibleJB):
                partial2 = random.sample([i for i in basic_items if i not in assignments[12]], max(1,min(len(possibleJB), random.randint(1, 12 - (len(partial4) + len(partial3))))))
            else:
                partial2 = random.sample(possibleJB, max(1,min(len(possibleJB), random.randint(1, 12 - (len(partial4) + len(partial3))))))
            for item in partial2:
                assignments[10].append(item)
                assignments[11].append(item)
                assignments[12].append(item)
                if (item in unique_items):
                    done_already.add(item)
            #pick a handful of items for first partial bar, include in all bard
            possibleJP = get_valid_items(item_reserve, jpshop, assignments[12])
            if not (possibleJP):
                partial1 = random.sample([i for i in basic_items if i not in assignments[12]], min(len(possibleJP), random.randint(1, 15 - (len(partial4) + len(partial3) + len(partial2)))))
            else:
                partial1 = random.sample(possibleJP, min(len(possibleJP), random.randint(1, 15 - (len(partial4) + len(partial3) + len(partial2)))))
            for item in partial1:
                assignments[9].append(item)
                assignments[10].append(item)
                assignments[11].append(item)
                assignments[12].append(item)
                if (item in unique_items):
                    done_already.add(item)


            #Randomly assign unique items until they've all been assigned.
            while len(done_already) < len(unique_items):
                #Get a random shop - avoided simple looping to prevent biasing against lategame shops
                shop1 = random.choice([items.MushroomKingdomShop, items.RoseTownArmorShop, items.RoseTownItemShop, items.MolevilleShop, items.MarrymoreShop, items.SeaShop, items.SeasideWeaponShop, items.SeasideAccessoryShop, items.SeasideArmorShop, items.SeasideItemShop, items.MonstroTownShop, items.NimbusLandShop, items.HinopioShop, items.BabyGoombaShop, items.NimbusLandItemWeaponShop, items.CrocoShop1, items.CrocoShop2, items.ToadShop])
                #this is really bad implementation but i don't know how else to get the world property to stop breaking for linear mode
                for shop2 in world.shops:
                    if shop2.index == shop1.index:
                        shop = shop2
                if len(assignments[shop.index]) < 15:
                    #Get all remaining items that can go in this shop
                    valid_items = get_valid_items(unique_items, shop)
                    #Pick one at random
                    if valid_items:
                        chosen_item = random.choice(valid_items)
                        assignments[shop.index].append(chosen_item)
                        done_already.add(chosen_item)
                remaining = [i for i in unique_items if i not in done_already]

            #Randomly assign anything to Yaridovich shop
            for shop in world.shops:
                if shop.index == 8:
                    valid_items = get_valid_items(item_reserve, shop)
                    yarid_items = random.sample(valid_items, random.randint(1, min(len(valid_items), 15)))
                    for item in yarid_items:
                        assignments[shop.index].append(item)

            #Assign random consumables to shops that have space left and can have consumables
            for shop1 in [items.MushroomKingdomShop, items.RoseTownItemShop, items.MolevilleShop, items.MarrymoreShop, items.SeaShop, items.SeasideItemShop, items.MonstroTownShop, items.NimbusLandShop, items.BabyGoombaShop, items.NimbusLandItemWeaponShop, items.CrocoShop1, items.CrocoShop2, items.ToadShop]:
                #this is really bad implementation but i don't know how else to get the world property to stop breaking for linear mode
                for shop2 in world.shops:
                    if shop2.index == shop1.index:
                        shop = shop2
                if len(assignments[shop.index]) < 15:
                    #guarantee pick me up in toad shop if not full
                    for item in world.items:
                        if item.index == 102 and shop.index == 24:
                            if (item not in assignments[shop.index] and item in shop_items):
                                assignments[shop.index].append(item)
                    if world.settings.is_flag_enabled(flags.ShopShuffleBalanced):
                        valid_consumables = get_valid_items(basic_items, shop, assignments[shop.index])
                    else:
                        valid_consumables = basic_items
                    max_remaining = min(15 - len(assignments[shop.index]), len(valid_consumables))
                    if max_remaining > 0:
                        append_consumables = random.sample(valid_consumables, random.randint(1, max_remaining))
                        for item in append_consumables:
                            if (item not in assignments[shop.index]):
                                assignments[shop.index].append(item)

            #Randomly assign anything to shops with space remaining
            done_already.clear()
            for shop in world.shops:
                if shop.index not in [3, 6, 8, 9, 10, 11, 12]:
                    if len(assignments[shop.index]) < 15:
                        valid_items = get_valid_items(unique_items, shop, assignments[shop.index])
                        if (valid_items):
                            max_remaining = min(15 - len(assignments[shop.index]), len(valid_items))
                            append_items = random.sample(valid_items, random.randint(1, max_remaining))
                            for item in append_items:
                                assignments[shop.index].append(item)

            #Loop through shops to find any that are empty, and just add Pick Me Up
            for shop in world.shops:
                if not (isinstance(shop, items.PartialJuiceBarShop) or shop.index in [disciple_shop, frog_coin_emporium]):
                    if not assignments[shop.index]:
                        assignments[shop.index].append(items.PickMeUp)

            # ******************************* Phase 3: Repricing

            for shop in world.shops:
                assigned_items = assignments[shop.index]
                for item in assigned_items:

                    # Turn the item into a frog coin price if it's in one of those shops.

                    ########Set new regular-coin prices for FC items

                    if world.settings.is_flag_enabled(flags.FreeShops):
                        if shop.frog_coin_shop:
                            item.frog_coin_item = True
                            item.price = 1
                        else:
                            item.price = 1
                    else:
                        if item.is_equipment:
                            if shop.frog_coin_shop:
                                item.frog_coin_item = True
                                item.price = max(math.ceil(item.rank_value / 5), 1)
                            else:
                                #Change constant to a lower value if items seem generally too expensive, or increase it if too cheap. Will affect better items more than bad ones
                                price = math.ceil(item.rank_value * (2 + (item.rank_order_reverse / len(ranks_reverse))))
                                price = utils.mutate_normal(price, minimum=price*0.9, maximum=price*1.1)
                                item.price = price
                        else:
                            if shop.frog_coin_shop:
                                item.frog_coin_item = True
                                price = utils.mutate_normal(item.price, minimum=item.price*0.9, maximum=item.price*1.1)
                                item.price = max(math.ceil(price / 25), 1)
                            else:
                                price = min(9999, max(2, item.price))
                                price = utils.mutate_normal(price, minimum=item.price*0.9, maximum=item.price*1.1)
                                item.price = price


            # Sort the list of items by the ordering rank for display, and assign to the shop.
            for shop in world.shops:
                shop.items = sorted(assignments[shop.index], key=lambda i: i.order)

    else:
        for shop in world.shops:
            if world.settings.is_flag_enabled(flags.FreeShops):
                for item in shop.items:
                    if shop.frog_coin_shop:
                        item.frog_coin_item = True
                        item.price = 1
                    else:
                        item.price = 1
                        
    
    if world.settings.is_flag_enabled(flags.PoisonMushroom):
        for item in world.items:
            if item.index == 175:
                item.status_immunities = [random.randint(0,7)]
