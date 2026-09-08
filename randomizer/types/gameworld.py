# pyright: reportWildcardImportFromLibrary=false
from __future__ import annotations
from randomizer.types.world_errors import (WorldBuildingException)
from typing import TYPE_CHECKING, Any, Callable, Type, TypeVar, cast
from copy import (deepcopy)


from .flags import *
from .check_flags import *  # EnabledRegularChecks, EnabledBossChecks, ShuffledBosses
from smrpgpatchbuilder.datatypes.battle_animation_scripts.types import (
    AnimationScriptBank,
)
from smrpgpatchbuilder.datatypes.battle_animation_scripts.commands import *
from smrpgpatchbuilder.datatypes.battle_animation_scripts.arguments import *
from smrpgpatchbuilder.datatypes.battles.battle_dialog_collection import (
    BattleDialogCollection,
)
from smrpgpatchbuilder.datatypes.dialogs.classes import DialogCollection
from smrpgpatchbuilder.datatypes.enemies.classes import EnemyCollection
from smrpgpatchbuilder.datatypes.enemy_attacks.classes import EnemyAttackCollection
from smrpgpatchbuilder.datatypes.items.classes import (
    ItemCollection,
    Equipment,
    RegularItem,
)
from smrpgpatchbuilder.datatypes.monster_scripts.commands import *
from smrpgpatchbuilder.datatypes.monster_scripts.arguments import *
from smrpgpatchbuilder.datatypes.monster_scripts.types import (
    MonsterScriptBank,
    MonsterScript,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.classes import (
    ActionScriptBank,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.classes import (
    EventScriptController,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.types.packet import (
    PacketCollection,
)
from smrpgpatchbuilder.datatypes.battles.formations_packs.types.classes import (
    PackCollection,
)
from smrpgpatchbuilder.datatypes.levels.room_collection import RoomCollection
from smrpgpatchbuilder.datatypes.shops.classes import ShopCollection
from smrpgpatchbuilder.datatypes.spells.classes import SpellCollection
from smrpgpatchbuilder.datatypes.graphics.classes import (SpriteCollection)
from smrpgpatchbuilder.datatypes.sprites.palette import (
    EventPaletteCollection,
    SpritePaletteCollection,
)
from smrpgpatchbuilder.datatypes.scripts_common.classes import IdentifierException
from smrpgpatchbuilder.datatypes.battles.formations_packs.types.classes import (
    FormationMember,
    Formation,
)
from smrpgpatchbuilder.datatypes.allies.ally_collection import AllyCollection
from smrpgpatchbuilder.datatypes.world_map_locations.classes import (
    WorldMapLocationCollection,
)
from ..data.items.items import *
from .item import Item
from .patch import Patch
from .spell import Spell
from .prize import (ItemPrize)
from .ally import Ally

# TypeVar for spell types to allow CharacterSpell and other Spell subclasses
SpellT = TypeVar("SpellT", bound=Spell)
from .prizelocation import (PrizeLocation)
# ThreeMustyFears proxy classes come from prizelocations via the wildcard import below
from randomizer.logic.progression.prizelocations import *
from ..data.variables.dialog_names import *
from ..data.variables.battle_variable_names import *
from ..data.variables.battle_effect_names import *
from ..data.variables.shop_names import *
from ..data.variables.sprite_names import *
from ..data.spells.spells import *
from randomizer.logic.build_world import build_world
from randomizer.logic.queries import (is_monstro_item, is_location_enabled, allocate_formation_id)
from randomizer.logic.rom.build_patch import get_patch as _build_rom_patch
from ..logic.spoiler.build_spoiler import build_spoiler

from ..data.allies.palettes.types import (
    MarioPalette,
    MallowPalette,
    GenoPalette,
    BowserPalette,
    ToadstoolPalette,
)
from ..data.allies.palettes.mario import MarioDefault
from ..data.allies.palettes.mallow import MallowDefault
from ..data.allies.palettes.geno import GenoDefault
from ..data.allies.palettes.bowser import BowserDefault
from ..data.allies.palettes.toadstool import ToadstoolDefault
from .enemy import Enemy

PrizeLocationT = TypeVar("PrizeLocationT", bound=PrizeLocation)
from .settings import Settings
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.types import AreaObject

if TYPE_CHECKING:
    from randomizer.logic.partition_calculator import VanillaRoomState


def get_flag_string_from_flag_collection(categories: list) -> str:
    """Placeholder for flag string generation."""
    return ""

class NumberThresholdFlag(RangeFlag):
    """Alias for range flags used as thresholds."""

    pass


class GameWorld:
    seed: int | str = 0
    settings: Settings
    file_select_names: list[str] = ["MARIO1", "MARIO2", "MARIO3", "MARIO4"]

    version: str = "9.0.0"
    hash: str = ""

    @property
    def file_select_hash(self) -> str:
        return " / ".join(self.file_select_names).replace("}", "-")

    # Raw data types (basis of ROM patches)

    allies: AllyCollection
    battle_animations: dict[int, AnimationScriptBank]
    battle_dialogs: BattleDialogCollection
    overworld_dialogs: DialogCollection
    enemies: EnemyCollection
    enemy_attacks: EnemyAttackCollection
    items: ItemCollection
    monster_scripts: MonsterScriptBank
    event_scripts: EventScriptController
    action_scripts: ActionScriptBank
    packets: PacketCollection
    battle_packs: PackCollection
    rooms: RoomCollection
    shops: ShopCollection
    spells: SpellCollection[Spell]
    sprites: SpriteCollection
    event_palettes: EventPaletteCollection
    sprite_palettes: SpritePaletteCollection
    mario_palette: MarioPalette = MarioDefault()
    mallow_palette: MallowPalette = MallowDefault()
    geno_palette: GenoPalette = GenoDefault()
    bowser_palette: BowserPalette = BowserDefault()
    toadstool_palette: ToadstoolPalette = ToadstoolDefault()
    main_character: Ally = MARIO_Ally
    file_select_character: str = "MARIO"
    world_map_locations: WorldMapLocationCollection
    password: str = "pearls"
    poison_mushroom_status: str | None = None
    song_1: str = "So La Mi Re Do Re Do Re"
    song_2: str = "Mi Do So Do Re La Ti Do"
    song_3: str = "La Ti Do Re So Do Re Mi"
    password_author: str = "ANONYMOUS"
    song_authors: list[str] = ["ANONYMOUS"]

    # Text-based shop items (set by shuffle_shops)
    room_service_items: list[type] = [PickMeUpItem, KerokeroColaItem]
    room_service_prices: list[int] = []  # Compensated prices (set by shuffle_shops)
    bomb_shop_items: list[type] = [FrightBombItem, FireBombItem, IceBombItem]

    locations: dict[type[PrizeLocation], PrizeLocation]
    chest_locations: list[PrizeLocation]
    standard_locations: list[PrizeLocation]
    coin_locations: list[PrizeLocation]
    spell_locations: list[PrizeLocation]
    boss_fight_locations: list[PrizeLocation]
    star_piece_locations: list[PrizeLocation]
    extra_star_piece_locations: list[PrizeLocation]
    key_item_locations: list[PrizeLocation]
    extra_key_item_locations: list[PrizeLocation]
    character_recruitment_locations: list[PrizeLocation]

    # Prize lookup cache: maps prize type -> location holding that prize
    # Updated via notify_prize_placed() when prizes are assigned
    _prize_type_to_location: dict[type, PrizeLocation]
    # Cache version - incremented when any prize is placed, used to invalidate caches
    _placement_version: int

    # Item impact categories (built by _build_item_impact_categories)
    low_impact_items: list[type[RegularItem]]
    high_impact_items: list[type[RegularItem]]
    highest_impact_items: list[type[RegularItem]]
    low_impact_equip: list[type[Equipment]]
    high_impact_equip: list[type[Equipment]]
    highest_impact_equip: list[type[Equipment]]
    equipment_ranks: list[tuple[type[Equipment], float]]

    # Mapping from item class to prize class (built by _build_item_to_prize_mapping)
    item_to_prize: dict[type[Item], type[ItemPrize]]

    # Music IDs for boss shuffle (built by apply_cosmetic_settings)
    selected_music_ids: list[int]

    # Cached placement, in. When set, _shuffle_items applies it instead of running place(), which is ~94% of build time
    placement_cache: bytes | None = None
    # Cached placement, out. Captured when the search finishes so it also records where the search left the RNG stream
    placement_result: bytes | None = None

    # Progress callback for SSE streaming (set by __init__)
    _progress_callback: Callable[[str, int], None] | None

    # Invisible item locations - stored separately to allow reuse across shuffle retries
    # These are initialized once during the first call to set_locations, then reused
    _invisible_item_locations: dict[type[PrizeLocation], PrizeLocation] | None = None

    # Dummy NPC index tracking for deterministic object presence table
    # Pre-allocated once by _pre_allocate_dummy_npcs, then reused across shuffle retries
    _slot_dummy_indices: dict[int, int] | None = None   # room_id → starting object index of 5 slot dummies
    _flag_dummy_index: dict[int, int] | None = None     # room_id → object index of 1 flag dummy

    _invisible_summoner_base: list | None = None

    _invisible_flag_choice: list[type] | None = None

    # Vanilla room NPC states for change detection during partition recalculation
    # Populated by snapshot_vanilla_room_states() before NPC shuffling begins
    _vanilla_room_states: dict[int, "VanillaRoomState"] | None = None

    # Last-resort switch for place()'s stall repair. False for every ordinary
    # attempt, so a seed that builds today builds identically; build_world turns
    # it on for one extra attempt after the retry budget is spent, rather than
    # giving up on a placement a swap could still rescue.
    allow_placement_repair: bool = False

    # Spell assignment tracking for SpellsAnywhere mode
    # Maps character prize type -> count of spells assigned to that character
    _spell_assignments: dict[type, int] | None = None

    # Cached random character-fill for the current shuffle attempt. shuffle_rules
    # is called many times per attempt (once per location in the pull loop); the
    # cache keeps the selected roster stable across those calls so spell-pool and
    # reward-location decisions stay consistent. Reset per attempt in shuffle_prizes.
    _cached_char_fill: list[type[CharacterPrize]] | None = None

    # The character promoted to the progression tier to satisfy Bowser's Keep's
    # damage spell gate. Cached and reset alongside _cached_char_fill.
    _cached_spell_damage_char: type[CharacterPrize] | None = None

    # The StartingCharacters flag's Random_X slots resolved to concrete allies,
    # drawn from the roster so a random starter is always a character the seed
    # contains. Resolving it more than once per attempt would hand the starter
    # locations a different party than the roster and spell pool were built for,
    # so it is cached and reset alongside _cached_char_fill.
    _cached_starting_chars: list[Ally] | None = None

    # Cached spell pool for the current shuffle attempt. Same reason as
    # _cached_char_fill: select_spells() picks at random, and re-rolling it on
    # every shuffle_rules() call desyncs the tier assignment between calls.
    _cached_spells: list[type[Prize]] | None = None

    # How many times each prize class has been handed out by
    # RandomPrizeSubstitute this shuffle attempt. Drawing from the least-used
    # classes keeps a ~158-draw fill from dumping three copies of the same
    # weapon into one seed. Reset per attempt in shuffle_prizes.
    substitute_draw_counts: dict[type[ItemPrize], int]

    @property
    def overworld_character(self) -> CharacterPrize:
        if not self.settings.isflag_enabled(PlayAsStarter):
            return MarioRecruitmentPrize()
        s = self.get_location(StartingCharacter1)
        assert s is not None
        assert isinstance(s.prize, CharacterPrize)
        return s.prize

    def _report_progress(self, message: str, percent: int) -> None:
        """Report progress to the callback if one is set."""
        if self._progress_callback:
            self._progress_callback(message, percent)

    @classmethod
    def is_remake_item(cls, item_type: type) -> bool:
        """Check if an item type is a special Monstro Town item."""
        return item_type in (
            WonderChompItem,
            Stella023Item,
            SageStickItem,
            EnduringBroochItem,
            TeamworkBandItem,
            ExtraShinyStoneItem,
            CrystalShardItem,
        )

    def get_item(self, item: int | type):
        if isinstance(item, int):
            i = next((i for i in self.items.items if i.item_id == item), None)
        else:
            i = next((i for i in self.items.items if isinstance(i, item)), None)
        assert i is not None, f"Item {item} does not exist in ItemCollection"
        return i

    def get_enemy(self, enemy_id: int | type[Enemy]):
        if isinstance(enemy_id, int):
            e = next(
                (e for e in self.enemies.enemies if e.monster_id == enemy_id), None
            )
        else:
            e = next((e for e in self.enemies.enemies if isinstance(e, enemy_id)), None)
        assert e is not None, f"Enemy {enemy_id} does not exist in EnemyCollection"
        return e

    def get_attack(self, attack_id: int | type[Attack]):
        if isinstance(attack_id, int):
            a = next(
                (a for a in self.enemy_attacks.attacks if a.index == attack_id), None
            )
        else:
            a = next(
                (a for a in self.enemy_attacks.attacks if isinstance(a, attack_id)),
                None,
            )
        assert (
            a is not None
        ), f"Attack {attack_id} does not exist in EnemyAttackCollection"
        return a

    def get_spell(self, spell_id: int | Type[SpellT]) -> Spell:
        if isinstance(spell_id, int):
            s = next((s for s in self.spells.spells if s.index == spell_id), None)
        else:
            s = next((s for s in self.spells.spells if isinstance(s, spell_id)), None)
        assert s is not None, f"Spell {spell_id} does not exist in SpellCollection"
        return s

    def get_dialog(self, dialog_id: int):
        d = self.overworld_dialogs.dialogs[dialog_id]
        assert d is not None, f"Dialog {dialog_id} does not exist in DialogCollection"
        return d

    def update_dialog(self, dialog_id: int, new_dialog: str):
        self.overworld_dialogs.replace_dialog(dialog_id, new_dialog)

    def get_battle_dialog(self, dialog_id: int):
        d = self.battle_dialogs.battle_dialogs[dialog_id]
        assert (
            d is not None
        ), f"Battle Dialog {dialog_id} does not exist in BattleDialogCollection"
        return d

    def get_location(self, location_type: type[PrizeLocationT]) -> PrizeLocationT:
        """Get a location instance with proper typing."""
        return cast(PrizeLocationT, self.locations[location_type])

    def notify_prize_placed(self, location: PrizeLocation, prize) -> None:
        """Notify that a prize was placed - updates caches.

        Call this after setting a prize on a location to keep caches in sync.
        """
        if prize is not None:
            # Index by prize's exact type (not parent classes) for precise lookup
            self._prize_type_to_location[type(prize)] = location
        self._placement_version += 1

    def get_location_by_prize_type(self, prize_type: type) -> PrizeLocation | None:
        """Get the location containing a prize of the exact given type (O(1) lookup).

        Returns None if no location has a prize of that exact type.
        """
        return self._prize_type_to_location.get(prize_type)

    @property
    def placement_version(self) -> int:
        """Current placement version - changes whenever a prize is placed.

        Use this to invalidate caches that depend on prize placements.
        """
        return self._placement_version

    def update_battle_dialog(self, dialog_id: int, new_dialog: str):
        self.battle_dialogs.battle_dialogs[dialog_id] = new_dialog

    def get_monster_script(self, script: int | Enemy):
        if isinstance(script, int):
            return self.monster_scripts.scripts[script]
        else:
            return self.monster_scripts.scripts[script.monster_id]

    def update_monster_script(self, script: int | Enemy, new_script: MonsterScript):
        if isinstance(script, int):
            self.monster_scripts.replace_script(script, new_script)
        else:
            self.monster_scripts.replace_script(script.monster_id, new_script)

    def get_event_script(self, event_script_id: int):
        return self.event_scripts.get_script_by_id(event_script_id)

    def get_action_script(self, action_script_id: int):
        return self.action_scripts.scripts[action_script_id]

    def get_battle_animation_command_by_name(self, command_name: str):
        try:
            return self.battle_animations[0x02].get_command_by_name(command_name)
        except IdentifierException:
            try:
                return self.battle_animations[0x35].get_command_by_name(command_name)
            except IdentifierException:
                try:
                    return self.battle_animations[0x3A].get_command_by_name(
                        command_name
                    )
                except IdentifierException:
                    raise WorldBuildingException("No battle animation banks found")

    def get_packet(self, packet_id: int):
        p = self.packets.packets[packet_id]
        assert p is not None, f"Packet {packet_id} does not exist in PacketCollection"
        return p

    def update_packet(self, packet_id: int, new_packet):
        self.packets.packets[packet_id] = new_packet

    _next_formation_id: int | None = None

    def get_battle_pack(self, pack_id: int):
        p = self.battle_packs.packs[pack_id]
        assert p is not None, f"Battle Pack {pack_id} does not exist in PackCollection"
        return p

    def update_battle_pack(self, pack_id: int, new_pack):
        self.battle_packs.packs[pack_id] = new_pack

    def replace_battle_pack_formations(
        self, members: list[FormationMember | None], pack_id: int
    ):
        pack = self.get_battle_pack(pack_id)
        if len(pack.formations) == 0:
            pack._formations = [Formation(members)]
            return
        formation_base = pack.formations[0]
        formation_base._members = members
        pack._formations = [formation_base]
        self.update_battle_pack(pack_id, pack)

    def get_room(self, room_id: int):
        r = self.rooms._rooms[room_id]
        assert r is not None, f"Room {room_id} does not exist in RoomCollection"
        return r

    def update_room(self, room_id: int, new_room):
        self.rooms._rooms[room_id] = new_room

    def get_shop(self, shop_id: int):
        s = self.shops.shops[shop_id]
        assert s is not None, f"Shop {shop_id} does not exist in ShopCollection"
        return s

    def update_shop(self, shop_id: int, new_shop):
        self.shops._shops[shop_id] = new_shop

    def get_sprite(self, sprite_id: int):
        s = self.sprites.sprites[sprite_id]
        assert s is not None, f"Sprite {sprite_id} does not exist in SpriteCollection"
        return s

    def update_sprite(self, sprite_id: int, new_sprite):
        self.sprites.sprites[sprite_id] = new_sprite

    def search_replace_dialog(self, search: str, replace: str):
        for bank_id, dialog_bank in enumerate(self.overworld_dialogs.raw_data):
            for index, dialog in enumerate(dialog_bank):
                self.overworld_dialogs.raw_data[bank_id][index] = dialog.replace(
                    search, replace
                )

    event_2496_startup = []

    @property
    def spoiler(self) -> dict[str, Any]:
        return build_spoiler(self)


    def __init__(
        self,
        seed: int | str,
        version: str,
        settings: Settings,
        allies: AllyCollection,
        battle_animations: dict[int, AnimationScriptBank],
        battle_dialogs: BattleDialogCollection,
        overworld_dialogs: DialogCollection,
        enemies: EnemyCollection,
        enemy_attacks: EnemyAttackCollection,
        items: ItemCollection,
        monster_scripts: MonsterScriptBank,
        event_scripts: EventScriptController,
        action_scripts: ActionScriptBank,
        packets: PacketCollection,
        battle_packs: PackCollection,
        rooms: RoomCollection,
        shops: ShopCollection,
        spells: SpellCollection[Spell],
        sprites: SpriteCollection,
        world_map_locations: WorldMapLocationCollection,
        event_palettes: EventPaletteCollection,
        sprite_palettes: SpritePaletteCollection,
        progress_callback: Callable[[str, int], None] | None = None,
        debug_bps_patches: bool = False,
        placement_cache: bytes | None = None,
    ):
        self._progress_callback = progress_callback
        self.placement_cache = placement_cache
        self.placement_result = None
        self._report_progress("Parsing settings...", 0)
        self.allies = allies
        self.seed = seed
        self.version = version
        self.settings = settings
        self._prize_type_to_location = dict()
        self._placement_version = 0
        self.battle_animations = battle_animations
        self.battle_dialogs = battle_dialogs
        self.overworld_dialogs = overworld_dialogs
        self.enemies = enemies
        self.enemy_attacks = enemy_attacks
        self.items = items
        self.monster_scripts = monster_scripts
        self.event_scripts = event_scripts
        self.action_scripts = action_scripts
        self.packets = packets
        self.battle_packs = battle_packs
        self.rooms = deepcopy(rooms)
        self.shops = shops
        self.spells = spells
        self.sprites = sprites
        self.world_map_locations = world_map_locations
        self._cached_patch: Patch | None = None
        self._debug_bps_patches = debug_bps_patches
        self.event_palettes = event_palettes
        self.sprite_palettes = sprite_palettes
        
        self.pending_sprite_blob: bytes | None = None
        self.sprite_writes: list[tuple[int, bytes]] | None = None
        self.sprite_reclaim_banks: list[tuple[int, int]] | None = None

        build_world(self)


    def _finalize_character_stats(self, ally) -> None:
        """Finalize character starting stats based on starting level and optimal choices."""
        pass


    def offer_sprite_blob(self, blob: bytes | None) -> None:
        """Offer a stored sprite render for the next get_patch() to replay"""
        self.pending_sprite_blob = blob

    def get_patch(self) -> Patch:
        """Assemble the ROM patch. Implementation lives in logic/rom/build_patch.py."""
        return _build_rom_patch(self)

    @classmethod
    def is_monstro_item(cls, item_type: type) -> bool:
        return is_monstro_item(item_type)

    def is_location_enabled(self, location_type) -> bool:
        return is_location_enabled(self, location_type)

    def allocate_formation_id(self) -> int:
        return allocate_formation_id(self)

