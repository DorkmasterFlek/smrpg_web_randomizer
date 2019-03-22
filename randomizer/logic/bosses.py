# Boss randomization logic for open mode.

import random
import statistics

from randomizer.data import bosses, enemies
from . import flags


def _boss_star_piece_filter(world, location):
    """Filter function for boss location star piece shuffle based on whether Culex and/or Bowser's Keep is included.

    Args:
        world (randomizer.logic.main.GameWorld):
        location (randomizer.data.bosses.StarLocation):

    Returns:
        bool: True is location is okay to be included, False otherwise.

    """
    if not isinstance(location, bosses.StarLocation):
        return False
    if isinstance(location, bosses.Culex) and not world.settings.is_flag_enabled(flags.CulexStarShuffle):
        return False
    if isinstance(location, bosses.BowsersKeepLocation) and not world.settings.is_flag_enabled(flags.BowsersKeepOpen):
        return False
    return True


def _boss_fight_filter(world, location):
    """

    Args:
        world (randomizer.logic.main.GameWorld):
        location (randomizer.data.bosses.BossLocation):

    Returns:
        bool: True is location is okay to be included, False otherwise.

    """
    if not isinstance(location, bosses.BossLocation):
        return False
    if isinstance(location, bosses.Culex) and not world.settings.is_flag_enabled(flags.BossShuffleCulex):
        return False
    return True


def randomize_all(world):
    """Randomize all the boss settings for the world.

    Args:
        world (randomizer.logic.main.GameWorld): Game world to randomize.

    """
    # Open mode-specific shuffles.
    if world.open_mode:
        # Shuffle boss star locations.
        if world.settings.is_flag_enabled(flags.StarPieceShuffle):
            for boss in world.boss_locations:
                boss.has_star = False

            possible_stars = [b for b in world.boss_locations if _boss_star_piece_filter(world, b)]

            # Check if we're doing 6 or 7 stars.
            num_stars = 7 if world.settings.is_flag_enabled(flags.SevenStarHunt) else 6
            star_bosses = random.sample(possible_stars, num_stars)
            for boss in star_bosses:
                boss.has_star = True

        # Shuffle boss encounters.
        if world.settings.is_flag_enabled(flags.BossShuffle):
            locations = [b for b in world.boss_locations if _boss_fight_filter(world, b)]
            shuffled_locations = locations[:]
            random.shuffle(shuffled_locations)
            shuffled_packs = [b.pack for b in shuffled_locations]

            # Randomize boss music for locations if enabled.
            if world.settings.is_flag_enabled(flags.BossShuffleMusic):
                # noinspection PyTypeChecker
                music_choices = list(bosses.BattleMusic)
                for location in locations:
                    location.music = random.choice(music_choices)

            # Scale boss stats accordingly if keep stats not enabled.
            if not world.settings.is_flag_enabled(flags.BossShuffleKeepStats):
                # First calculate total stats for each slot based on anchors and stats shuffled already.
                location_stats = []
                for location in locations:
                    elist = location.formation.stat_total_enemies
                    # HP
                    # For Exor fight, only count Exor and average of Left + Right Eye mandatory HP.
                    if any(e for e in elist if isinstance(e, enemies.Exor)):
                        hp = 0
                        eyes = 0
                        for e in elist:
                            if isinstance(e, enemies.Exor):
                                hp += e.hp
                            elif isinstance(e, (enemies.LeftEye, enemies.RightEye)):
                                eyes += e.hp
                        hp += int(eyes / 2)
                        xp = sum(e.xp for e in elist if isinstance(e, enemies.Exor))
                        coins = sum(e.coins for e in elist if isinstance(e, enemies.Exor))
                    # For Cloaker/Domino, count average HP of each phase of the fight.
                    elif any(e for e in elist if isinstance(e, enemies.Cloaker)):
                        dudes = 0
                        sneks = 0
                        for e in elist:
                            if isinstance(e, (enemies.Cloaker, enemies.Domino)):
                                dudes += e.hp
                            elif isinstance(e, (enemies.Earthlink, enemies.MadAdder)):
                                sneks += e.hp
                        hp = int(round((dudes / 2) + (sneks / 2)))
                        xp = sum(e.xp for e in elist if isinstance(e, enemies.Cloaker) or isinstance(e, enemies.Domino))
                        coins = sum(e.coins for e in elist if isinstance(e, enemies.Cloaker) or isinstance(e, enemies.Domino))
                    # For Dodo/Valentina, count 40% of Dodo's HP.
                    elif any(e for e in elist if isinstance(e, enemies.Valentina)):
                        dodo = 0
                        valentina = 0
                        for e in elist:
                            if isinstance(e, enemies.Dodo):
                                dodo += e.hp * 0.4
                            elif isinstance(e, enemies.Valentina):
                                valentina += e.hp
                        hp = int(round(dodo + valentina))
                        xp = sum(e.xp for e in elist)
                        coins = sum(e.coins for e in elist)
                    # For King Calimari, need special exp calc
                    elif any(e for e in elist if isinstance(e, enemies.KingCalamari)):
                        hp = sum(e.hp for e in elist)
                        xp = sum(e.xp for e in elist if isinstance(e, enemies.KingCalamari))
                        coins = sum(e.coins for e in elist if isinstance(e, enemies.KingCalamari))
                    # For Megasmilax, need special exp calc
                    elif any(e for e in elist if isinstance(e, enemies.Megasmilax)):
                        hp = sum(e.hp for e in elist)
                        xp = sum(e.xp for e in elist if isinstance(e, enemies.Megasmilax))
                        coins = sum(e.coins for e in elist if isinstance(e, enemies.Megasmilax))
                    # For Axems, need special exp calc
                    elif any(e for e in elist if isinstance(e, enemies.AxemRangers)):
                        hp = sum(e.hp for e in elist)
                        xp = sum(e.xp for e in elist if isinstance(e, enemies.AxemRangers))
                        coins = sum(e.coins for e in elist if isinstance(e, enemies.AxemRangers))
                    # For Belome 2, need special exp calc
                    elif any(e for e in elist if isinstance(e, enemies.Belome2)):
                        hp = sum(e.hp for e in elist)
                        xp = sum(e.xp for e in world.enemies if isinstance(e, enemies.Belome2) or isinstance(e, enemies.MarioClone))
                        coins = sum(e.coins for e in world.enemies if isinstance(e, enemies.Belome2) or isinstance(e, enemies.MarioClone))
                    # For Culex, need special exp calc
                    elif any(e for e in elist if isinstance(e, enemies.Culex)):
                        hp = sum(e.hp for e in elist)
                        xp = sum(e.xp for e in world.enemies if isinstance(e, enemies.Culex) or isinstance(e, enemies.WindCrystal) or isinstance(e, enemies.WaterCrystal) or isinstance(e, enemies.FireCrystal) or isinstance(e, enemies.EarthCrystal))
                        coins = sum(e.coins for e in world.enemies if isinstance(e, enemies.Culex) or isinstance(e, enemies.WindCrystal) or isinstance(e, enemies.WaterCrystal) or isinstance(e, enemies.FireCrystal) or isinstance(e, enemies.EarthCrystal))
                    # For Johnny, need special exp calc
                    elif any(e for e in elist if isinstance(e, enemies.Johnny)):
                        hp = sum(e.hp for e in elist)
                        xp = 0
                        coins = 0
                        for e in world.enemies:
                            if isinstance(e, (enemies.Johnny)):
                                xp += e.xp
                                coins += e.coins
                            elif isinstance(e, (enemies.BandanaBlue)):
                                xp += 4 * e.xp
                                coins += 4 * e.coins
                    # Anything else, just sum all HP/xp/coins.
                    else:
                        hp = sum(e.hp for e in elist)
                        xp = sum(e.xp for e in elist)
                        coins = sum(e.coins for e in elist)

                    # For other stats, if there's an anchor then take that enemy's stats.  Otherwise average them.
                    anchor = location.formation.shuffle_anchor
                    if anchor:
                        attack = anchor.attack
                        defense = anchor.defense
                        magic_attack = anchor.magic_attack
                        magic_defense = anchor.magic_defense
                        evade = anchor.evade
                        magic_evade = anchor.magic_evade
                    else:
                        attack = int(round(statistics.mean(e.attack for e in elist)))
                        defense = int(round(statistics.mean(e.defense for e in elist)))
                        magic_attack = int(round(statistics.mean(e.magic_attack for e in elist)))
                        magic_defense = int(round(statistics.mean(e.magic_defense for e in elist)))
                        evade = int(round(statistics.mean(e.evade for e in elist)))
                        magic_evade = int(round(statistics.mean(e.magic_evade for e in elist)))

                    location_stats.append({
                        'hp': hp,
                        'attack': attack,
                        'defense': defense,
                        'magic_attack': magic_attack,
                        'magic_defense': magic_defense,
                        'evade': evade,
                        'magic_evade': magic_evade,
                        'xp': xp,
                        'coins': coins,
                    })

                # Now adjust stats for each shuffled pack given the total stats for the slot it's going into.
                for location, stats in zip(shuffled_locations, location_stats):
                    for i, enemy in enumerate(location.formation.stat_scaling_enemies):
                        # Do not raise King Bomb's stats more than normal.
                        no_raise = isinstance(enemy, enemies.KingBomb)

                        enemy.hp = min(int(round(stats['hp'] * enemy.ratio_hp)), enemy.hp if no_raise else 65535)
                        enemy.attack = min(int(round(stats['attack'] * enemy.ratio_attack)),
                                           enemy.attack if no_raise else 255)
                        enemy.defense = min(int(round(stats['defense'] * enemy.ratio_defense)),
                                            enemy.defense if no_raise else 255)
                        enemy.magic_attack = min(int(round(stats['magic_attack'] * enemy.ratio_magic_attack)),
                                                 enemy.magic_attack if no_raise else 255)
                        enemy.magic_defense = min(int(round(stats['magic_defense'] * enemy.ratio_magic_defense)),
                                                  enemy.magic_defense if no_raise else 255)
                        enemy.evade = min(int(round(stats['evade'] * enemy.ratio_evade)), 100)
                        enemy.magic_evade = min(int(round(stats['magic_evade'] * enemy.ratio_magic_evade)), 100)

                        # For snek fight, the XP/coins need to be put on Cloaker/Domino 2 because you fight either one.
                        if location.formation.index == 309:
                            if isinstance(enemy, (enemies.Cloaker2, enemies.Domino2)):
                                enemy.xp = min(stats['xp'], 0xffff)
                                enemy.coins = min(stats['coins'], 255)
                            else:
                                enemy.xp = 0
                                enemy.coins = 0
                        # For Countdown fight, use the Ding-A-Lings because Countdown disables himself.
                        elif location.formation.index == 295:
                            if isinstance(enemy, enemies.DingALing):
                                enemy.xp = min(int(round(stats['xp'] / 2)), 0xffff)
                                enemy.coins = min(int(round(stats['coins'] / 2)), 255)
                            else:
                                enemy.xp = 0
                                enemy.coins = 0
                        # Otherwise give the first enemy all the XP/coins, except for Hammer Bros that need half.
                        elif i == 0:
                            if isinstance(enemy, enemies.HammerBro):
                                enemy.xp = min(int(round(stats['xp'] / 2)), 0xffff)
                                enemy.coins = min(int(round(stats['coins'] / 2)), 255)
                            else:
                                enemy.xp = min(stats['xp'], 0xffff)
                                enemy.coins = min(stats['coins'], 255)
                        else:
                            enemy.xp = 0
                            enemy.coins = 0

            # Assign packs to their new locations and update music and can't run flags.
            for location, pack in zip(locations, shuffled_packs):
                location.pack = pack
                location.formation.music = location.music
                location.formation.can_run_away = location.can_run_away

                # *** Special cases

                # Hide Shelly and show Birdo instead to skip first phase if not in vanilla location.
                # TODO: Should we bother with this???
                # if location.formation.index == 297 and not isinstance(location, bosses.Birdo):
                #     location.formation.members[0].hidden_at_start = False
                #     location.formation.members[1].hidden_at_start = True

                # For Boomer fight, "hide" the Hangin' Shy enemies by moving them off the screen.  This is needed
                # because they set bits for the Boomer fight and disable themselves.  Also make sure speed is max.
                if location.formation.index == 358 and not isinstance(location, bosses.Boomer):
                    location.formation.members[1].x_pos = 0
                    location.formation.members[1].y_pos = 255
                    location.formation.members[2].x_pos = 0
                    location.formation.members[2].y_pos = 255

            # *** Certain formation changes necessary for boss shuffle.

            # Formation 368 is a solo Mad Mallet fight before the factory boss rush.
            # These enemies need to be changed to some other factory enemies when doing boss shuffle.
            factory_enemies = [
                enemies.LilBoo,
                enemies.MachineMadeShyster,
                enemies.Puppox,
                enemies.Doppel,
                enemies.Hippopo,
            ]
            formation = world.get_enemy_formation_by_index(368)
            for member in formation.members:
                member.enemy = random.choice(factory_enemies)

    # *** Make sure certain enemies always have max speed for required battle scripts!

    # Valentina calls Dodo.
    world.get_enemy_instance(enemies.Valentina).speed = 255

    # Axem's ship sets bits and disables itself in phase one.
    world.get_enemy_instance(enemies.AxemRangers).speed = 255

    # Hangin' Shy enemies set Boomer bits and disable themselves.
    world.get_enemy_instance(enemies.HanginShy).speed = 255

    # Exor goes first to set immunity.
    world.get_enemy_instance(enemies.Exor).speed = 255
