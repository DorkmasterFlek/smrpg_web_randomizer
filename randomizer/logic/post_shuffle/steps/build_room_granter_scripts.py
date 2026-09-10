"""Build the per-room event scripts that grant prizes and launch boss fights.

Extracted from the apply_shuffler_results orchestrator.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from randomizer.data.physical_objects.items import (
    CoinStillObject,
    DefaultItem,
    FlowerItemObject,
    FlowerObject,
    FrogCoinAnimatedObject,
    FrogCoinItemObject,
    FrogCoinObject,
    RecoveryMushroomObject,
    SmallCoinItemObject,
    SmallCoinStillObject,
    SmallFrogCoinObject,
)
from randomizer.data.rooms.npcs import (EMPTY_NPC, SHARED_ITEM_BASE)
from randomizer.data.variables.dialog_names import (
    DI2908_TREASURE_SELLER_ITEM_2,
    DI2911_TREASURE_SELLER_ITEM_1,
    DI2914_TREASURE_SELLER_ITEM_3,
)
from randomizer.data.variables.event_script_names import (
    E0005_FREESTANDING_BIG_COIN_ROOM_AWARE,
    E0167_BOSS_GRANT_STAR_PIECE,
    E0227_FREESTANDING_15_GRANT,
    E0241_FREESTANDING_1_GRANT,
    E0353_BOSS_BATTLE,
    E1810_TEMPLE_VAULT_LOADER,
    E3146_FREESTANDING_BIG_COIN,
    E3885_END_GAME,
)
from randomizer.data.variables.room_names import (
    R159_STAR_HILL_AREA_04,
    R422_BELOME_TEMPLE_AREA_09_BELOMES_TREASURE_ROOM,
    R496_FACTORY_GROUNDS_FIGHT_WITH_SMITHY_USES_SLEDGE,
)
from randomizer.data.variables.sprite_names import (
    SPR0050_BOOSTER,
    SPR0055_JONATHAN_JONES,
    SPR0189_CROCO_STILL,
    SPR0190_CROCO_OVERWORLD,
    SPR0191_JINX_OVERWORLD_1,
    SPR0392_PUNCHINELLO_2,
    SPR0431_JOHNNY_2,
    SPR0457_BELOME_3RD_TIME,
    SPR0470_FANCY_BUNDT,
    SPR0583_PANDORITE_SMALL,
    SPR0584_HIDON_SMALL,
    SPR0585_CHESTER_SMALL,
    SPR0586_BOX_BOY_SMALL,
    SPR0589_BELOME_SMALL,
    SPR0590_BELOME_SMALL,
    SPR0592_PUNCHINELLO_SMALL,
    SPR0607_JINX_OVERWORLD_2,
    SPR0608_JINX_OVERWORLD_3,
    SPR0633_CULEX_SMALL,
    SPR0672_BELOME_2_LARGE_OVERWORLD,
    SPR0721_BUNDT_OBJECT_MAYBE,
    SPR0727_JINX_OVERWORLD_4,
    SPR0736_BELOME_3_SMALL,
    SPR0737_PUNCHINELLO_2_SMALL,
    SPR0738_BOOSTER_2_SMALL,
    SPR0739_JOHNNY_2_SMALL,
    SPR0740_BUNDT_2_SMALL,
    SPR0742_CULEX_2_SMALL,
    SPR0753_PUNCHINELLO_POSTGAME_2,
    SPR0755_BELOME_3_LARGE_2,
    SPR0757_BUNDT_2_LARGE_2,
    SPR0759_JOHNNY_2_LARGE_2,
)
from randomizer.data.variables.variable_names import (
    BOSS_VICTORY_COUNTER,
    GAME_OVER,
    RUN_AWAY,
    PRIMARY_TEMP_7000,
    SHIP_PACKET_AUTOTERM_DIALOG,
    SMITHY_BOSS_HUNT_WIN_CONDITION,
    STAR_PIECE_GRANT_DIRECTIONAL_BIT,
    STAR_PIECE_GRANT_DIRECTIONAL_BIT_2,
)
from randomizer.logic.partition_calculator import (snapshot_vanilla_room_states)
from randomizer.logic.renders import (apply_ending_characters)
from randomizer.logic.progression.prizelocations import (
    ForestMazeCharacter,
    InnerMinesCharacter,
    MarrymoreCharacter,
    Mimic3BossFight,
    MushroomWayCharacter,
    StarHillStarPiece,
    StartingCharacter1,
    StartingCharacter2,
    StartingCharacter3,
    StartingCharacter4,
    StartingCharacter5,
    TreasureShopItem1,
    TreasureShopItem2,
    TreasureShopItem3,
)
from randomizer.logic.progression.prizes import (
    BowserRecruitmentPrize,
    GenoRecruitmentPrize,
    MallowRecruitmentPrize,
    MarioRecruitmentPrize,
    SmithyBossFight,
    ToadstoolRecruitmentPrize,
)
from randomizer.types.flags import (
    AvailableCharacters,
    DifferentiateRepeatedBosses,
    PlayAsStarter,
)
from randomizer.types.physical_objects import (ItemNPC)
from randomizer.types.prize import (
    BossFightPrize,
    CharacterPrize,
    FrogCoinPrize,
    ItemPrize,
    SlotsPrize,
    StandardPrize,
)
from randomizer.types.prizelocation import (
    BoosterHillLocation,
    BossFightLocation,
    CharacterRecruitmentLocation,
    EventLocation,
    PrizeRow,
    ROOM_TO_BATTLEFIELD,
    RiverLocation,
    StandingLocation,
    StarPieceLocation,
    TreasureChestLocation,
    TreasureShopLocation,
)
from smrpgpatchbuilder.datatypes.levels.classes import (
    BaseRoomObject,
    BufferType,
    ChestClone,
    ChestNPC,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.commands import (
    A_IncPaletteRowBy,
    A_SequencePlaybackOn,
    A_SetSpriteSequence,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.commands.types.classes import (
    UsableActionScriptCommand,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments import (NORTHWEST)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import (NPC_9)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.types.area_object import (AreaObject)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import (
    ActionQueueSync,
    ClearBit,
    EnterArea,
    Inc,
    JmpIfBitClear,
    JmpIfBitSet,
    JmpIfVarEqualsConst,
    JmpToEvent,
    ResetAndChooseGame,
    Return,
    Set7000ToCurrentLevel,
    StartBattleAtBattlefield,
    SummonObjectToSpecificLevel,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands.types.classes import (
    UsableEventScriptCommand,
)
from typing import (cast)
from uuid import (uuid4)

if TYPE_CHECKING:
    from randomizer.types.gameworld import GameWorld


# Belome's treasury holds fifteen freestanding prizes in one room. Every model its
# allowlist admits is a non-gridplane sprite, so each distinct sprite_id costs its
# own dedicated VRAM allocation from the $6D cursor. Put every prize on ONE sprite
# (SPR0846, which carries all five graphics as molds) so the whole room spends a
# single allocation, and pick the graphic per object at load time.
_SHARED_MOLD_ROOM = R422_BELOME_TEMPLE_AREA_09_BELOMES_TREASURE_ROOM
_SHARED_MOLDS: dict[type[ItemNPC], int] = {
    FlowerObject: 0,
    FlowerItemObject: 0,
    RecoveryMushroomObject: 1,
    DefaultItem: 2,
    CoinStillObject: 3,
    FrogCoinObject: 3,
    SmallCoinStillObject: 4,
    SmallCoinItemObject: 4,
    FrogCoinItemObject: 4,
    SmallFrogCoinObject: 4,
}
# Frog coins are the coin molds recoloured: same tiles, palette 8+2 = SPAL010.
# A_IncPaletteRowBy(2) moves the object to the CGRAM row holding it -- see
# SHARED_ITEM_BASE, which loads the extra rows that makes that row real.
_SHARED_FROG_COIN_MODELS = (FrogCoinObject, FrogCoinItemObject, SmallFrogCoinObject)
_SHARED_FROG_COIN_PALETTE_ROWS = 2


def build_room_granter_scripts(world: GameWorld) -> None:
    builders: dict[
        int, tuple[list[UsableEventScriptCommand], list[UsableEventScriptCommand]]
    ] = {}
    henchman_container_events: set[int] = set()
    # Snapshot vanilla NPC states before any shuffling modifies room objects
    snapshot_vanilla_room_states(world)

    # When repeated bosses shouldn't be visually differentiated, copy palette
    # IDs from a canonical source sprite onto each duplicate/variant sprite
    # so they share overworld coloring. Must run before location render so
    # downstream renderers (e.g. KeepAfterObstaclesBossFight setting event
    # palettes 24/25) read the unified palette IDs.
    if not world.settings.isflag_enabled(DifferentiateRepeatedBosses):
        sprite_palette_copies: list[tuple[int, int]] = [
            (SPR0190_CROCO_OVERWORLD, SPR0189_CROCO_STILL),
            (SPR0607_JINX_OVERWORLD_2, SPR0191_JINX_OVERWORLD_1),
            (SPR0608_JINX_OVERWORLD_3, SPR0191_JINX_OVERWORLD_1),
            (SPR0727_JINX_OVERWORLD_4, SPR0191_JINX_OVERWORLD_1),
            (SPR0590_BELOME_SMALL, SPR0589_BELOME_SMALL),
            (SPR0736_BELOME_3_SMALL, SPR0589_BELOME_SMALL),
            (SPR0739_JOHNNY_2_SMALL, SPR0055_JONATHAN_JONES),
            (SPR0737_PUNCHINELLO_2_SMALL, SPR0592_PUNCHINELLO_SMALL),
            (SPR0740_BUNDT_2_SMALL, SPR0721_BUNDT_OBJECT_MAYBE),
            (SPR0742_CULEX_2_SMALL, SPR0633_CULEX_SMALL),
            (SPR0738_BOOSTER_2_SMALL, SPR0050_BOOSTER),
            (SPR0583_PANDORITE_SMALL, SPR0586_BOX_BOY_SMALL),
            (SPR0584_HIDON_SMALL, SPR0586_BOX_BOY_SMALL),
            (SPR0585_CHESTER_SMALL, SPR0586_BOX_BOY_SMALL),
            (SPR0753_PUNCHINELLO_POSTGAME_2, SPR0392_PUNCHINELLO_2),
            (SPR0755_BELOME_3_LARGE_2, SPR0457_BELOME_3RD_TIME),
            (SPR0672_BELOME_2_LARGE_OVERWORLD, SPR0457_BELOME_3RD_TIME),
            (SPR0757_BUNDT_2_LARGE_2, SPR0470_FANCY_BUNDT),
            (SPR0759_JOHNNY_2_LARGE_2, SPR0431_JOHNNY_2),
        ]
        for target_id, source_id in sprite_palette_copies:
            source_palette_id = world.get_sprite(source_id).palette_id
            world.get_sprite(target_id).palette_id = source_palette_id

    shared_mold_queue: list[tuple[AreaObject, int, int]] = []

    for place in world.locations.values():
        # skip frog disciple locations, they're set in shop shuffler
        if isinstance(place, (BossFightLocation, PrizeRow, StarPieceLocation)):
            ctr = place._container_event
            if ctr not in builders:
                builders[ctr] = ([], [])
            if isinstance(place, BossFightLocation):
                decision, execution, henchmen_packs = place.render(world)
                for container_event, room_id, pack_id in henchmen_packs:
                    henchman_container_events.add(container_event)
                    if container_event not in builders:
                        builders[container_event] = ([], [])
                    identifier = str(uuid4())
                    builders[container_event][0].append(
                        JmpIfVarEqualsConst(PRIMARY_TEMP_7000, room_id, [identifier])
                    )
                    builders[container_event][1].extend([
                        StartBattleAtBattlefield(pack_id, ROOM_TO_BATTLEFIELD[room_id], identifier=identifier),
                        Return(),
                    ])
            else:
                decision, execution = place.render(world)
            d_flat = [cmd for l in decision for cmd in l]
            builders[ctr][0].extend(d_flat)

            # Smithy fight needs special post-battle handling: set TEMP_704A_2
            # and jump to E1011 instead of returning, so the game over / run away
            # check works correctly for multi-phase Smithy battles.
            if isinstance(place.prize, SmithyBossFight):
                patched: list[UsableEventScriptCommand] = []
                for i, cmd in enumerate(execution):
                    patched.append(cmd)
                    if isinstance(cmd, StartBattleAtBattlefield) and i + 1 < len(execution) and isinstance(execution[i + 1], Return):
                        disabled_label = f"smithy_boss_hunt_disabled_{uuid4()}"
                        disabled_label_ra = f"smithy_boss_hunt_disabled_{uuid4()}_ra"
                        patched.extend([
                            JmpIfBitSet(GAME_OVER, [disabled_label_ra]),
                            JmpIfBitSet(RUN_AWAY, [disabled_label]),
                            JmpIfBitClear(SMITHY_BOSS_HUNT_WIN_CONDITION, [disabled_label]),
                            EnterArea(room_id=R496_FACTORY_GROUNDS_FIGHT_WITH_SMITHY_USES_SLEDGE, face_direction=NORTHWEST, x=4, y=48, z=0, run_entrance_event=False),
                            JmpToEvent(E3885_END_GAME),
                            Return(identifier=disabled_label),
                            # Locations whose launching script handles GAME_OVER itself
                            # (the dojo fights) must not reset here -- just return and let
                            # the caller decide, the way every non-Smithy prize does.
                            ResetAndChooseGame(identifier=disabled_label_ra)
                            if place.resets_on_game_over
                            else Return(identifier=disabled_label_ra),
                        ])
                    elif isinstance(cmd, Return) and i > 0 and isinstance(execution[i - 1], StartBattleAtBattlefield):
                        continue  # Skip the Return that follows StartBattle
                execution = patched

            builders[ctr][1].extend(execution)

            if isinstance(place.prize, SlotsPrize):
                # special handling: battlefield selection for failed slot machines which fights mimic #3
                proxy_fight = cast(BossFightLocation, world.get_location(Mimic3BossFight))
                slot_pack = proxy_fight.slots_pack_id
                assert slot_pack is not None
                room = place._rooms[0]
                battlefield = ROOM_TO_BATTLEFIELD[room]
                proxy_prize = cast(BossFightPrize, proxy_fight.prize)
                if proxy_prize.force_battlefield is not None:
                    battlefield = proxy_prize.force_battlefield
                identifier = str(uuid4())
                if E0353_BOSS_BATTLE not in builders:
                    builders[E0353_BOSS_BATTLE] = ([], [])
                builders[E0353_BOSS_BATTLE][0].append(JmpIfVarEqualsConst(PRIMARY_TEMP_7000, place.prize.override_id, [identifier]))
                builders[E0353_BOSS_BATTLE][1].extend([
                    StartBattleAtBattlefield(slot_pack, battlefield, identifier=identifier),
                    Return(),
                ])
            
            if isinstance(
                place, (StandingLocation, EventLocation, RiverLocation)
            ) and not isinstance(place, BoosterHillLocation):
                npcs = []
                if hasattr(place, "_npc_ids") and hasattr(place, "_rooms"):
                    npcs = zip(place._npc_ids, place._rooms)  # type: ignore
                for n, room_id_int in npcs:
                    npc = cast(AreaObject, n)
                    room = world.rooms._rooms[room_id_int]
                    assert room is not None, f"Room {room_id_int} not found"
                    if room_id_int == _SHARED_MOLD_ROOM and place.prize is not None:
                        # Shared-mold room: render every prize from SPR0195/SPR0846
                        # and pick the graphic with a mold instead of a sprite_id.
                        # The vanilla guard below is deliberately skipped here --
                        # keeping a location's original NPC would reintroduce the
                        # very sprite_id this exists to remove, and the shared molds
                        # reproduce the same graphic anyway.
                        prize_model = place.prize.model
                        if prize_model is None or (
                            place._model_allowlist is not None
                            and not issubclass(prize_model, tuple(place._model_allowlist))
                        ):
                            prize_model = DefaultItem
                        mold = _SHARED_MOLDS.get(prize_model, _SHARED_MOLDS[DefaultItem])
                        room_obj = room.get_npc_by_target_id(npc)
                        assert room_obj is not None, f"NPC {npc} not found in room {room_id_int}"
                        cast(BaseRoomObject, room_obj)._npc = SHARED_ITEM_BASE
                        palette_rows = (
                            _SHARED_FROG_COIN_PALETTE_ROWS
                            if issubclass(prize_model, _SHARED_FROG_COIN_MODELS)
                            else 0
                        )
                        shared_mold_queue.append((npc, mold, palette_rows))
                        continue
                    # Vanilla guard: if the placed prize is the location's own
                    # original prize, leave the room's NPC untouched so its
                    # sprite isn't swapped for a different-looking model (e.g. a
                    # vanilla SMALL_COIN_NPC -> SMALL_COIN_STILL_BASE).
                    if place.originally_held is not None and isinstance(
                        place.prize, place.originally_held
                    ):
                        continue
                    if place.prize is not None and place.prize.model is not None:
                        prize_model = place.prize.model
                        if place._model_allowlist is not None and not issubclass(prize_model, tuple(place._model_allowlist)):
                            prize_model = DefaultItem
                        # Frog coins: swap the (allowlist-approved) static frog
                        # coin for the animated FROG_COIN_BASE variant only when
                        # the room has a Coins partition in buffer C, which the
                        # animation needs. Rendering detail; keeps DefaultItem if
                        # the allowlist rejected the frog coin above.
                        if isinstance(place.prize, FrogCoinPrize) and prize_model is FrogCoinObject:
                            buffers = room.partition.buffers if room.partition is not None else []
                            if len(buffers) >= 3 and buffers[2].buffer_type == BufferType.COINS:
                                prize_model = FrogCoinAnimatedObject
                        model = prize_model().base
                    else:
                        model = EMPTY_NPC
                    room_obj = room.get_npc_by_target_id(npc)
                    assert room_obj is not None, f"NPC {npc} not found in room {room_id_int}"
                    cast(BaseRoomObject, room_obj)._npc = model

            if isinstance(place, StarHillStarPiece):
                # Show the star piece on Star Hill if it's set
                if place.prize is not None:
                    world.event_2496_startup.append(
                        SummonObjectToSpecificLevel(NPC_9, R159_STAR_HILL_AREA_04)
                    )
            if isinstance(place, TreasureChestLocation) and isinstance(place.prize, ItemPrize):
                item_id = place.prize.item().item_id
                for npc, room_id in zip(place._npc_ids, place._rooms):
                    ao = npc if isinstance(npc, AreaObject) else AreaObject(npc + 0x14)
                    room = world.rooms._rooms[room_id]
                    if room is not None:
                        room_obj = room.get_npc_by_target_id(ao)
                        if isinstance(room_obj, (ChestNPC, ChestClone)):
                            room_obj.set_lower_70a7(item_id & 0x0F)
                            room_obj.set_upper_70a7((item_id >> 4) & 0x0F)
            if isinstance(place, TreasureShopLocation) and isinstance(place.prize, StandardPrize):
                if hasattr(place.prize, "_nickname"):
                    nn = place.prize.nickname
                    if isinstance(place, TreasureShopItem1):
                        world.update_dialog(DI2911_TREASURE_SELLER_ITEM_1, nn.get_slot_1_dialog())
                    elif isinstance(place, TreasureShopItem2):
                        world.update_dialog(DI2908_TREASURE_SELLER_ITEM_2, nn.get_slot_2_dialog())
                    elif isinstance(place, TreasureShopItem3):
                        world.update_dialog(DI2914_TREASURE_SELLER_ITEM_3, nn.get_slot_3_dialog())

        elif isinstance(place, CharacterRecruitmentLocation):
            # this takes care of everything for character gating and recruitment
            place.render(world)

    # Point each shared-mold prize at its graphic. This goes in the room's entrance
    # event so it re-runs every time the player walks back in.
    #
    # Two things here are load-bearing, and both were learned the hard way:
    #
    # 1. The queues go at the TOP, above E1810's own JmpIfBitSet, so they run on
    #    both branches and before the tail JmpToEvent(E0015). E0015 command 12 is
    #    FadeInFromBlack -- queue a mold after that and it is applied to a room the
    #    player can already see, racing them for control. Only some land, and how
    #    many varies with the queue lengths a given seed happens to produce.
    # 2. They are ActionQueueSync (blocking), not Async. Async issues all fifteen
    #    and falls straight through to the fade, so the molds lose the race and
    #    every object shows its default mold 0. Blocking makes the fade wait until
    #    every mold has switched -- which is the whole point of running before it.
    #
    # Inserted in reverse so that repeated insertion at index 0 leaves the queue in
    # its original order.
    if shared_mold_queue:
        loader = world.get_event_script(E1810_TEMPLE_VAULT_LOADER)
        for target, mold, palette_rows in reversed(shared_mold_queue):
            # Sequence, not mold. SPR0846 carries one single-frame sequence per mold,
            # so sequence N shows mold N. A mold is a one-shot write that later
            # sprite init can clobber; a sequence is persistent state the engine
            # re-applies, so it should survive whatever is resetting the later
            # objects. Playback has to be ON or the sequence never gets applied --
            # which is also why the old A_SequencePlaybackOff is gone.
            subscript: list[UsableActionScriptCommand] = [
                A_SequencePlaybackOn(),
                A_SetSpriteSequence(index=mold, is_mold=False, looping=True),
            ]
            if palette_rows:
                # Recolour the coin molds green for frog coins.
                subscript.append(A_IncPaletteRowBy(palette_rows))
            loader.insert_before_nth_command(
                0, ActionQueueSync(target=target, subscript=subscript)
            )

    # Render the four ending-cutscene character slots. Each named recruitment
    # location maps to a render_ending_character_N function; empty named slots
    # are filled from a substitute pool that combines StartingCharacterX prizes
    # with stand-in prizes for any character excluded from the seed via the
    # AvailableCharacters flag.
    def _char_prize(loc_class: type) -> CharacterPrize | None:
        if loc_class not in world.locations:
            return None
        loc = world.get_location(loc_class)
        if loc is None or loc.prize is None:
            return None
        assert isinstance(loc.prize, CharacterPrize)
        return loc.prize

    starter_prizes: list[CharacterPrize] = [
        p
        for p in (
            _char_prize(StartingCharacter1),
            _char_prize(StartingCharacter2),
            _char_prize(StartingCharacter3),
            _char_prize(StartingCharacter4),
            _char_prize(StartingCharacter5),
        )
        if p is not None
    ]

    # Excluded characters have no prize anywhere in the world, so we
    # instantiate a stand-in CharacterPrize for each one and add it to the
    # substitute pool. This way they still get a slot (and palette) in the
    # ending cutscene.
    excluded_prize_classes_by_ally_name: dict[str, type[CharacterPrize]] = {
        "Mario": MarioRecruitmentPrize,
        "Mallow": MallowRecruitmentPrize,
        "Geno": GenoRecruitmentPrize,
        "Bowser": BowserRecruitmentPrize,
        "Toadstool": ToadstoolRecruitmentPrize,
    }
    excluded_prizes: list[CharacterPrize] = []
    for member in world.settings.get_flag(AvailableCharacters).disabled:
        ally = member.value
        prize_cls = excluded_prize_classes_by_ally_name.get(ally.name)
        if prize_cls is not None:
            excluded_prizes.append(prize_cls())

    # MaxCharacters can also drop characters from the seed (the items shuffler
    # picks at most N character prizes, leaving the rest unplaced). Those don't
    # show up in AvailableCharacters.disabled, so detect them by scanning every
    # location in the world and adding a stand-in for any character class that
    # has no prize anywhere.
    placed_character_classes: set[type[CharacterPrize]] = set()
    for loc in world.locations.values():
        if loc.prize is not None and isinstance(loc.prize, CharacterPrize):
            placed_character_classes.add(type(loc.prize))
    already_subbed = {type(p) for p in excluded_prizes}
    for prize_cls in excluded_prize_classes_by_ally_name.values():
        if prize_cls in placed_character_classes or prize_cls in already_subbed:
            continue
        excluded_prizes.append(prize_cls())

    # When PlayAsStarter is disabled, the player visually plays as Mario
    # everywhere outside of battle regardless of who the actual starter is.
    # If the starter (StartingCharacter1) is anyone but Mario, the ending
    # cutscene needs Mario's slot to render as the starter instead.
    mario_override: CharacterPrize | None = None
    if not world.settings.isflag_enabled(PlayAsStarter):
        starter_1_prize = _char_prize(StartingCharacter1)
        if starter_1_prize is not None and not isinstance(
            starter_1_prize, MarioRecruitmentPrize
        ):
            mario_override = starter_1_prize

    apply_ending_characters(
        world,
        mushroom_way_prize=_char_prize(MushroomWayCharacter),
        forest_maze_prize=_char_prize(ForestMazeCharacter),
        inner_mines_prize=_char_prize(InnerMinesCharacter),
        marrymore_prize=_char_prize(MarrymoreCharacter),
        substitute_prizes=starter_prizes + excluded_prizes,
        mario_override=mario_override,
        # Lock the cutscene protagonist to world.overworld_character - the
        # same source _apply_overworld_character_sprite_swap uses to pick
        # which NPC slot gets sprite 31. Both the script's protagonist-role
        # animations and the sprite-31 swap MUST target the same NPC slot,
        # otherwise the script animates one slot while sprite 31 lives on
        # another.
        protagonist_override=world.overworld_character,
    )

    for henchman_event in henchman_container_events:
        builders[henchman_event][0].insert(0,
            Set7000ToCurrentLevel(),
        )
    for key, (decision, execution) in builders.items():
        event_script = world.event_scripts.get_script_by_id(key)
        contents: list[UsableEventScriptCommand] = []
        if key == E0167_BOSS_GRANT_STAR_PIECE:
            contents.extend(
                [
                    ClearBit(STAR_PIECE_GRANT_DIRECTIONAL_BIT),
                    ClearBit(STAR_PIECE_GRANT_DIRECTIONAL_BIT_2),
                    Inc(BOSS_VICTORY_COUNTER),
                ]
            )
        if E0241_FREESTANDING_1_GRANT >= key >= E0227_FREESTANDING_15_GRANT:
            contents.insert(0, Set7000ToCurrentLevel())
            # Normalize the ship-packet auto-terminate signal before every freestanding
            # grant. The 5 auto-terminating Sunken Ship packets set it in their grant tail
            # (in execution below); clearing here guarantees it never leaks past one
            # collection, including on grant paths that show no "Got ..." dialog (star
            # piece, coins, flower) and so never clear it themselves.
            contents.insert(0, ClearBit(SHIP_PACKET_AUTOTERM_DIALOG))
        contents.extend([*decision, Return(), *execution])
        event_script.set_contents(contents)

        # Point big-coin grants at the room-aware wrapper. E0005 falls straight through
        # to E3146 for every room except 422, whose prizes share gridplane SPR0846 --
        # E3146 sets sequence 2, which is the item bag on that sprite. These containers
        # are shared across NINETEEN rooms, so the room test has to live inside E0005;
        # rewriting them to a 422-specific script strips the collect animation from the
        # other eighteen.
        if E0241_FREESTANDING_1_GRANT >= key >= E0227_FREESTANDING_15_GRANT:
            for cmd in event_script.contents:
                if (
                    isinstance(cmd, JmpToEvent)
                    and cmd.destination == E3146_FREESTANDING_BIG_COIN
                ):
                    cmd.set_destination(E0005_FREESTANDING_BIG_COIN_ROOM_AWARE)


__all__ = ['build_room_granter_scripts']
